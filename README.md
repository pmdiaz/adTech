# AdTech

Solucion al ejercicio final de la materia *PROGRAMACIÓN AVANZADA PARA GRANDES VOLÚMENES DE DATOS*

## Grupo:
- Pablo Diaz
- Martin Groppo
- Ezequiel Martinez
- Valentin Dualde

### Setup local:

```
git clone git@github.com:pmdiaz/adTech.git
cd adTech
./airflow/setup_airflow.sh
./airflow/start_airflow.sh          
```

### Para levantar airflow en Compute Engine:

```
git clone git@github.com:pmdiaz/adTech.git
cd adTech
cp .env.example .env
nano .env #Configurar user, pass, host y password de la base de datos
./airflow/init_instance.sh
./airflow/setup_airflow.sh
./airflow/start_airflow.sh cloud    # cloud (PostgreSQL, lee airflow/.env)
```

y para frenarlo:

```
./airflow/stop_airflow.sh
```
