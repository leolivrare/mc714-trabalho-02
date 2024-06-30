# Build completo do docker-compose sem cache
build-all:
	docker-compose build --no-cache

# Build apenas do lamport_app_1 e 2
build-apps:
	docker-compose build --no-cache lamport_app_1 lamport_app_2

# Colocar para executar todo o ambiente do kafka
run-kafka:
	docker-compose up -d broker schema-registry connect control-center ksqldb-server ksqldb-cli ksql-datagen rest-proxy

create-topic:
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic lamport_test_1

# Colocar para executar ambos os lamport_app_s
run-apps:
	docker-compose up -d lamport_app_1 lamport_app_2

# Comando para escutar os logs de ambos os lamport_app_s
logs-apps:
	docker-compose logs -f lamport_app_1 lamport_app_2

# Comando para escutar os logs de cada lamport_app_ separadamente
logs-app1:
	docker-compose logs -f lamport_app_1

logs-app2:
	docker-compose logs -f lamport_app_2

# Build apenas do serviço test
build-test:
	docker-compose build --no-cache test

run-tests:
	docker-compose up test

# Delete and recreate the Kafka topic
reset-topic:
	docker-compose exec broker kafka-topics --delete --bootstrap-server broker:29092 --topic lamport_test_1
	docker-compose exec broker kafka-topics --create --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic lamport_test_1

# Stop all running containers
stop:
	docker-compose down
