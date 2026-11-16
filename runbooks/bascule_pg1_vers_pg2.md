\# Runbook — Bascule pg1 (primaire) → pg2 (standby)



\## Contexte

Réplication physique en streaming entre pg1 (192.168.56.11) et pg2 (192.168.56.12).

En cas de panne de pg1, pg2 doit être promu en primaire.



\## Prérequis

\- pg1 primaire, pg2 standby

\- pg\_stat\_replication sur pg1 montre state = streaming



\## Étapes



\### 1. Vérifier que pg2 est à jour (sur pg1)

sudo -u postgres psql -c "SELECT pg\_wal\_lsn\_diff(pg\_current\_wal\_lsn(), replay\_lsn) FROM pg\_stat\_replication;"

→ doit renvoyer 0



\### 2. Simuler la panne de pg1 (sur pg1)

sudo systemctl stop postgresql@14-main.service



\### 3. Promouvoir pg2 (sur pg2)

sudo -u postgres pg\_ctl promote -D /var/lib/postgresql/14/main



\### 4. Vérifier que pg2 n'est plus en recovery (sur pg2)

sudo -u postgres psql -c "SELECT pg\_is\_in\_recovery();"

→ doit renvoyer f



\### 5. Vérifier que pg2 accepte les écritures (sur pg2)

sudo -u postgres psql -c "CREATE TABLE test\_bascule (id int);"



\## Reconstruction de pg1 en réplique (à détailler en Phase 4)

\- Arrêter pg1

\- Vider /var/lib/postgresql/14/main

\- pg\_basebackup depuis pg2

\- Démarrer pg1

