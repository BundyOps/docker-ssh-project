https://chat.deepseek.com/share/qtwgz8nhf2wr24ui9y





docker exec -it developer1 bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
ssh jump
ssh-add -l     # your key is here (forwarded)
ls ~/.ssh/     # only authorized_keys — no private key
ssh jump
dev1@jump$ ssh app-vm
dev1@app-vm$ curl nginx/health
dev1@app-vm$ curl app:8000/health


docker exec -it jump bash
ssh -L 127.0.0.1:8080:app:8000 dev@app-vm       or        ssh -L 127.0.0.1:8080:db:5432 dev@app-vm
curl localhost:8080/health


docker exec -it developer2 bash
ssh -L 127.0.0.1:8080:127.0.0.1:8080 dev@jump   or        psql -h 127.0.0.1 -p 8080 -U myuser myapp_db
