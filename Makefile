deploy: test
	ansible-playbook site.yml

test:
	ansible-playbook --check site.yml

deploy-dedibox:
	ansible-playbook -i dedibox, site.yml

test-dedibox:
	ansible-playbook -i dedibox, --check site.yml

deploy-dedibox-only-haproxy:
	false
	ansible-playbook -i dedibox, --check site.yml --extra-vars="host_roles=chmduquesne.haproxy"
