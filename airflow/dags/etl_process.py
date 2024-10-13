import datetime

from airflow.decorators import dag, task


markdown_text = """
### ETL Process for customer satisfaction dataset

This DAG extracts information from the original parquet file stored in the repository.

The dataset is splitted in training and testing (80/20).

It preprocesses the data by enconding features, creating dummy, treatment of outliers and missings imputation.
    
After preprocessing, the data is saved back into a S3 bucket as two separate CSV files: one for training and one for 
testing. 
"""

default_args = {
    'owner': "Grupo",
    'depends_on_past': False,
    'schedule_interval': None,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'dagrun_timeout': datetime.timedelta(minutes=15)
}


@dag(
    dag_id="process_etl",
    description="ETL process for customer satisfaction dataset.",
    doc_md=markdown_text,
    tags=["ETL", "Customer satisfaction"],
    default_args=default_args,
    catchup=False,
)

def process_etl():

    @task.virtualenv(
        task_id="obtain_original_data",
        requirements=["awswrangler==3.6.0"],
        system_site_packages=True
    )

    def get_data():
        import awswrangler as wr
        import pandas as pd
        # leemos el dataset que vamos a subir a s3
        ds = pd.read_parquet('../data/df_total.parquet')

        # lo subimos a s3
        data_path = "s3://data/raw/df_total.parquet"
        wr.s3.to_parquet(df=ds,
                        path=data_path,
                        index=False)
        
    @task.virtualenv(
        task_id="split_dataset",
        requirements=["awswrangler==3.6.0",
                      "scikit-learn==1.3.2"],
        system_site_packages=True
    )

    def split_dataset():
        # Dividimos el dataset en train y test (80/20)
        import pandas as pd
        import awswrangler as wr
        from sklearn.model_selection import train_test_split

        def save_to_csv(df, path):
            wr.s3.to_csv(df=df,
                         path=path,
                         index=False)

        data_original_path = "s3://data/raw/df_total.parquet"
        dataset = wr.s3.read_parquet(data_original_path)

        X = dataset.drop(columns='satisfaction')
        y = dataset[['satisfaction']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=42)
        df_train = pd.concat([X_train, y_train], axis=1).reset_index(drop=True)
        df_test = pd.concat([X_test, y_test], axis=1).reset_index(drop=True)

        save_to_csv(df_train, "s3://data/raw/df_train.csv")
        save_to_csv(df_test, "s3://data/raw/df_test.csv")

    @task.virtualenv(
        task_id="preprocess",
        requirements=["awswrangler==3.6.0"],
        system_site_packages=True
    )


    def preprocess():
        # Hacemos el pre procesamiento de las variables
        import awswrangler as wr
        import pandas as pd
        import numpy as np


        data_original_path_train = "s3://data/raw/df_train.csv"
        data_original_path_test = "s3://data/raw/df_test.csv"

        # Leemos los datasets 
        df_train = wr.s3.read_csv(data_original_path_train)
        df_test = wr.s3.read_csv(data_original_path_test)
        # Encodeamos la variable target
        df_train['target'] = np.where(df_train['satisfaction']=='satisfied',1,0)
        df_test['target'] = np.where(df_test['satisfaction']=='satisfied',1,0)
        df_train = df_train.drop(['satisfaction'], axis=1)
        df_test = df_test.drop(['satisfaction'], axis=1)
        #Encodeamos la variable Class que tiene un ordenamiento implícito
        def encode_class(input_string):  
            return input_string.replace('Eco', '0').replace('Eco Plus', '2').replace('Business', '3')  

        df_train['class_cus'] = encode_class(df_train['class_cus']) 
        df_test['class_cus'] = encode_class(df_test['class_cus']) 

        #Hacemos dummies de las variables categoricas
        df_train['gender_male'] = np.where(df_train['gender']=='Male',1,0)
        df_test['gender_male'] = np.where(df_test['gender']=='Male',1,0)

        df_train['customer_type_disloyal_customer'] = np.where(df_train['customer_type']=='disloyal Customer',1,0)
        df_test['customer_type_disloyal_customer'] = np.where(df_test['customer_type']=='disloyal Customer',1,0)

        df_train['type_of_travel_personal_travel'] = np.where(df_train['type_of_travel']=='Personal Travel',1,0)
        df_test['type_of_travel_personal_travel'] = np.where(df_test['type_of_travel']=='Personal Travel',1,0)

        #Imputamos missings a las variables
        df_train['arrival_delay_in_minutes'] = np.where(df_train['arrival_delay_in_minutes'].isnull(), df_train['departure_delay_in_minutes'], df_train['arrival_delay_in_minutes'])
        df_test['arrival_delay_in_minutes'] = np.where(df_test['arrival_delay_in_minutes'].isnull(), df_test['departure_delay_in_minutes'], df_test['arrival_delay_in_minutes'])

        #Generamos features adicionales
        for i in ['inflight_wifi_service', 'departure_arrival_time_convenient',	'ease_of_online_booking', 'online_boarding']:
            df_train[f'{i}_rta0'] = np.where(df_train[i]==0,1,0)
            df_test[f'{i}_rta0'] = np.where(df_test[i]==0,1,0)

        #Tratamiento de outliers
        for col in ['flight_distance', 'departure_delay_in_minutes', 'arrival_delay_in_minutes']:
                dict_q95 = {'flight_distance': 3376, 'departure_delay_in_minutes': 77, 'arrival_delay_in_minutes': 78}

                df_train[col]= np.where(df_train[col]>dict_q95[col], dict_q95[col], df_train[col])
                df_test[col]= np.where(df_test[col]>dict_q95[col], dict_q95[col], df_test[col])

        #Mantenemos en el dataset las features input del modelo
        features_input = ['age', 'class_cus', 'flight_distance', 'inflight_wifi_service',
       'departure_arrival_time_convenient', 'ease_of_online_booking',
       'gate_location', 'food_and_drink', 'online_boarding', 'seat_comfort',
       'inflight_entertainment', 'on_board_service', 'leg_room_service',
       'baggage_handling', 'checkin_service', 'inflight_service',
       'cleanliness', 'departure_delay_in_minutes', 'arrival_delay_in_minutes',
       'target', 'gender_male', 'customer_type_disloyal_customer',
       'type_of_travel_personal_travel', 'inflight_wifi_service_rta0',
       'departure_arrival_time_convenient_rta0', 'ease_of_online_booking_rta0',
       'online_boarding_rta0']
        
        df_train = df_train[features_input]
        df_test = df_test[features_input]

        def save_to_csv(df, path):
            wr.s3.to_csv(df=df,
                         path=path,
                         index=False)
            
        save_to_csv(df_train, "s3://data/clean/df_train_clean.csv")
        save_to_csv(df_test, "s3://data/clean/df_test_clean.csv")

    #get_data() >> split_dataset() >> preprocess()
    split_dataset() >> preprocess()


dag = process_etl()