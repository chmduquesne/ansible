ifneq (${TEST}, 0)
	CHECK=--check
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
	ansible-playbook --check ${INVENTORY} ${VARS} site.yml

deploy:
	ansible-playbook ${INVENTORY} ${VARS} site.yml

debug:
	@echo HOST=${HOST}
	@echo INVENTORY=${INVENTORY}
	@echo ROLE=${ROLE}
	@echo VARS=${VARS}
	@echo TEST=${TEST}
	@echo CHECK=${CHECK}
