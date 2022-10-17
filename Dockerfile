FROM python:3.8

WORKDIR /usr/src/polititweet

RUN pip install pipenv

COPY Pipfile ./

RUN pipenv lock
RUN pipenv install --system --deploy

COPY polititweet .

RUN SECRET_KEY=secretsecretsecret python manage.py collectstatic

RUN adduser \
    --disabled-password \
    --no-create-home \
    chequeado

EXPOSE 8080

#RUN chown chequeado:chequeado sqlite3.db
#RUN chmod 775 sqlite3.db

USER chequeado

CMD [ "./launch.sh" ]