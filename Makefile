ifneq (${TEST}, 0)
	CHECK=--check --diff
endif

ifdef HOST
	INVENTORY=-i ${HOST},
endif

ifdef ROLE
	VARS=--extra-vars="host_roles=${ROLE}"
endif

all:
	ansible-playbook ${CHECK} ${INVENTORY} ${VARS} site.yml

test:
	ansible-playbook --check --diff ${INVENTORY} ${VARS} site.yml

deploy:
	ansible-playbook ${INVENTORY} ${VARS} site.yml

debug:
	@echo HOST=${HOST}
	@echo INVENTORY=${INVENTORY}
	@echo ROLE=${ROLE}
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
	@echo   HOST=myhost ROLE=myrole make deploy
	@echo
	@echo Simulate deploying a role on a host:
	@echo   HOST=myhost ROLE=myrole make test
