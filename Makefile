# Build completo do docker-compose sem cache
build-all:
	docker-compose build --no-cache

# Build apenas do lamport_process_1 e 2
build-lamport-apps:
	docker-compose build --no-cache lamport_process_1 lamport_process_2

# Colocar para executar todo o ambiente do kafka
run-kafka:
	docker-compose up -d broker schema-registry connect control-center ksqldb-server ksqldb-cli ksql-datagen rest-proxy

create-lamport-topic:
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic lamport_test_1

# Colocar para executar ambos os lamport_process
run-lamport-apps:
	docker-compose up -d lamport_process_1 lamport_process_2

# Comando para escutar os logs de ambos os lamport_process_s
logs-lamport-apps:
	docker-compose logs -f lamport_process_1 lamport_process_2

# Comando para escutar os logs de cada lamport_process_ separadamente
logs-lamport-app1:
	docker-compose logs -f lamport_process_1

logs-lamport-app2:
	docker-compose logs -f lamport_process_2

# Build apenas do serviço test
build-lamport-test:
	docker-compose build --no-cache lamport_test

run-lamport-tests:
	docker-compose up lamport_test

# Build apenas do serviço test
build-mutual-exclusion-test:
	docker-compose build --no-cache mutual_exclusion_test

run-mutual-exclusion-tests:
	docker-compose up mutual_exclusion_test

# Delete and recreate the Kafka topic
reset-lamport-topic:
	docker-compose exec broker kafka-topics --delete --bootstrap-server broker:29092 --topic lamport_test_1
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic lamport_test_1

# Build apenas do mutual_exclusion_process_1, 2 e 3
build-mutual-exclusion-apps:
	docker-compose build --no-cache mutual_exclusion_process_1 mutual_exclusion_process_2 mutual_exclusion_process_3

create-mutual-exclusion-topic:
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic mutual_exclusion_test_1

# Colocar para executar ambos os mutual_exclusion_process
run-mutual-exclusion-apps:
	docker-compose up -d mutual_exclusion_process_1 mutual_exclusion_process_2 mutual_exclusion_process_3

# Comando para escutar os logs de todos os mutual_exclusion_process_s
logs-mutual-exclusion-apps:
	docker-compose logs -f mutual_exclusion_process_1 mutual_exclusion_process_2 mutual_exclusion_process_3

# Comando para escutar os logs de cada mutual_exclusion_process_ separadamente
logs-mutual-exclusion-app1:
	docker-compose logs -f mutual_exclusion_process_1

logs-mutual-exclusion-app2:
	docker-compose logs -f mutual_exclusion_process_2

logs-mutual-exclusion-app3:
	docker-compose logs -f mutual_exclusion_process_3

# Delete and recreate the Kafka topic for mutual exclusion
reset-mutual-exclusion-topic:
	docker-compose exec broker kafka-topics --delete --bootstrap-server broker:29092 --topic mutual_exclusion_test_1
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic mutual_exclusion_test_1

# Parar apenas as aplicações lamport
stop-lamport-apps:
	docker-compose stop lamport_process_1 lamport_process_2

# Parar apenas as aplicações mutual-exclusion
stop-mutual-exclusion-apps:
	docker-compose stop mutual_exclusion_process_1 mutual_exclusion_process_2 mutual_exclusion_process_3

# Stop all running containers
stop:
	docker-compose down
