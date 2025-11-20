Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices

flowchart TD

    A[Raw Hotel Service Sales Transactions<br/>(POS, JSON, CSV)] 
        --> B[GCP Cloud Storage<br/>(Raw Landing Bucket)]
        
    B --> C[Cloud Composer<br/>(Ingestion + Cleansing + Schema Formation)]

    C --> D[BigQuery<br/>(Raw Zone Table)]

    D --> E[DBT Core<br/>(Transformation & Feature Engineering)]

    E --> F[BigQuery<br/>(Curated / Analytical Tables)]
    
    F --> G[Vertex AI / Gemini<br/>(ML Model Training & Predictive Analytics)]
    
    G --> H[ML Predictions<br/>(Prediction Table in BigQuery)]

    H --> I[Looker Studio Dashboard<br/>+ Conversational Bot]

    I --> J[Hotel Managers<br/>Marketing Teams<br/>SME Partners]

