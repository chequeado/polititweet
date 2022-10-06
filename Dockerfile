FROM python:3.8

WORKDIR /usr/src/polititweet

RUN pip install pipenv

COPY Pipfile ./

RUN pipenv lock
RUN pipenv install --system --deploy

COPY polititweet .

RUN SECRET_KEY=secretsecretsecret python manage.py collectstatic

RUN chown -R root:root /usr/src/polititweet

EXPOSE 8080

CMD [ "./launch.sh" ]