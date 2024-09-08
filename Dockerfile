FROM python:3.11.8

ADD telegram.py . 
ADD alltokens.py .

RUN pip install aiogram==2.23.1
RUN pip install tgtg
RUN pip install supabase
CMD ["python", "./telegram.py"]