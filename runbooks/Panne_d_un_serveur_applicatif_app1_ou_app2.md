Runbook — Panne d'un serveur applicatif (app1 ou app2)


Contexte
HAProxy répartit le trafic HTTP entre app1 (192.168.56.20) et app2 (192.168.56.21) avec un contrôle de santé sur /health. Si une application tombe, le trafic doit être redirigé automatiquement sans interruption pour l'utilisateur.

Prérequis
app1 et app2 démarrés (Flask en écoute sur le port 5000).

HAProxy actif avec option httpchk GET /health.

Étapes
1. Vérifier l'état des backends (interface HAProxy)
Ouvrir dans un navigateur : http://192.168.56.100:8404/stats (admin/motdepasse_stats).
→ app1 et app2 doivent être en UP (vert).

2. Simuler la panne de app1 (sur app1)
bash
pkill -f app.py
3. Observer la bascule automatique
Après environ 6 secondes (3 checks x 2s), rafraîchir la page /stats.
→ app1 passe en DOWN (rouge), app2 reste UP (vert).

4. Vérifier la continuité de service (depuis le client Windows)
powershell
curl.exe http://192.168.56.100/health
→ doit toujours renvoyer {"status":"ok"} (servi par app2).

5. Remettre app1 en service (sur app1)
bash
cd /opt/app
nohup /opt/app/venv/bin/python app.py > /opt/app/flask.log 2>&1 &
→ après 6 secondes, app1 repasse UP dans HAProxy.