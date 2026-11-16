Runbook — Reconstruction de pg1 (ancien primaire) en standby

Contexte
Suite à une panne, pg1 a été réparé. pg2 est désormais le primaire actif. pg1 doit être réintégré dans l'architecture en tant que standby (réplique) de pg2. Réplication physique en streaming.

Prérequis
pg2 est le primaire actif (192.168.56.12).

pg1 est éteint ou arrêté (192.168.56.11).

Le slot de réplication slot_pg1 existe sur pg2.

Étapes
1. Créer le slot sur le nouveau primaire (sur pg2)
bash
sudo -u postgres psql -p 5433 -c "SELECT pg_create_physical_replication_slot('slot_pg1');"
→ doit renvoyer slot_pg1 | (avec un LSN).

2. Arrêter pg1 et vider ses données (sur pg1)
bash
sudo pg_ctlcluster 16 main stop
sudo rm -rf /var/lib/postgresql/16/main/*
3. Cloner pg2 vers pg1 (sur pg1)
bash
sudo -u postgres pg_basebackup -h 192.168.56.12 -p 5433 \
  -U replicator -D /var/lib/postgresql/16/main \
  -Fp -Xs -P -R -S slot_pg1
→ doit se terminer par pg_basebackup: base backup completed.

4. Démarrer pg1 en mode standby (sur pg1)
bash
sudo pg_ctlcluster 16 main start
5. Vérifier que pg1 est en recovery (sur pg1)
bash
sudo -u postgres psql -p 5433 -c "SELECT pg_is_in_recovery();"
→ doit renvoyer t.

6. Vérifier que la réplication est active (sur pg2)
bash
sudo -u postgres psql -p 5433 -c "SELECT client_addr, state FROM pg_stat_replication;"
→ doit renvoyer 192.168.56.11 | streaming.