https://chat.deepseek.com/share/qtwgz8nhf2wr24ui9y





docker exec -it developer bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
ssh jump
ssh-add -l     # your key is here (forwarded)
ls ~/.ssh/     # only authorized_keys — no private key
ssh dev@internal


