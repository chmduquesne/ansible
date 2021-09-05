ifdef host
	INVENTORY=-i ${host},
endif

ifdef role
	VARS=--extra-vars="host_roles=['${role}']"
endif

all: test

test:
	ansible-playbook --check --diff ${INVENTORY} ${VARS} deploy.yml

deploy:
	ansible-playbook ${INVENTORY} ${VARS} deploy.yml

run:
	ansible ${host} -a "${cmd}"

debug:
	@echo host=${host}
	@echo role=${role}
	@echo INVENTORY=${INVENTORY}
	@echo VARS=${VARS}
	@echo TEST=${TEST}
	@echo CHECK=${CHECK}

help:
	@echo Simulate all roles:
	@echo   make test
	@echo
	@echo Deploy all roles:
	@echo   make deploy
	@echo
	@echo Deploy a role on a host:
	@echo   host=myhost role=myrole make deploy
	@echo
	@echo Simulate deploying a role on a host:
	@echo   host=myhost role=myrole make test
