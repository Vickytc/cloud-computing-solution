# Use the base Python image as the starting point
FROM fission/python-env-3.9

# Set any environment variables if necessary
# ENV ENV_VARIABLE=value

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip


# Install any additional dependencies you need
RUN pip install elasticsearch8==8.11.0 aiokafka==0.8.0 Mastodon.py==1.8.1
RUN pip install textblob readability
RUN pip install wordcloud matplotlib


RUN pip install nltk 
RUN python -m nltk.downloader vader_lexicon


# RUN pip install spacy==3.0.6
# RUN python -m spacy download en_core_web_sm


# Copy your application code into the container
# COPY . /app
