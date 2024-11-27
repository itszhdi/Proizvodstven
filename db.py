import psycopg2
from contextlib import closing
try:
    with closing(psycopg2.connect(
            dbname='project',
            user='postgres',
            password='1234567',
            host='localhost',
            port='5432')) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                user_id SERIAL PRIMARY KEY,
                user_mail TEXT NOT NULL,
                user_password TEXT NOT NULL
            );
            
             CREATE TABLE IF NOT EXISTS Organizers (
                organizer_id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
            
            CREATE TABLE IF NOT EXISTS Categories (
                category_id SERIAL PRIMARY KEY,
                category VARCHAR(100)
            );

            CREATE TABLE IF NOT EXISTS Events (
                event_id SERIAL PRIMARY KEY,
                event_name VARCHAR(250) NOT NULL,
                event_date DATE NOT NULL,
                description TEXT,
                category_id INT NOT NULL REFERENCES Categories(category_id),
                organizer_id INT NOT NULL REFERENCES Organizers(organizer_id),
                city VARCHAR(100) NOT NULL,
                time VARCHAR(50) NOT NULL,
                address VARCHAR(100) NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS Tickets (
                ticket_id SERIAL PRIMARY KEY,
                event_id INT NOT NULL REFERENCES Events(event_id),
                user_id INT REFERENCES Customers(user_id),
                price INT NOT NULL
            );
            
            INSERT INTO Categories(category)
            VALUES ('ЧТО ГДЕ КОГДА'),
                   ('Music event'),
                   ('AITUSA event'),
                   ('Party'),
                   ('Competition');
            
            INSERT INTO Organizers(name)
            VALUES ('Mind Games'),
                   ('Music Club'),
                   ('AITUSA'),
                   ('Aitu Live');
            
            INSERT INTO Events(event_name, event_date, description, category_id, organizer_id, city, time, address)
            VALUES  ('Acoustic night', '19-04-2024', 'AITU Music Club invites you to a unique celebration of love and romance! Every year, on April 15th, Kazakhstan celebrates the magnificent holiday - Lovers` Day, inspired by the wonderful Kazakh legend of love «Kozy-Korpesh - Bayan-Sulu»', 2, 2, 'Astana', '18:00:00', 'Open Space'),
                    ('Miss & Mister AITU', '03-05-2024', 'Already on May 3, we will find out who will receive the title of Miss&Mister AITU at an exciting gala concert, where you are expected: Raffle of the merch and unique prizes from sponsors! (For more information, follow our stories)', 5, 3, 'Astana', '16:00:00', 'Assembly Hall'),
                    ('Финал осенней серии "Что? Где? Когда?"', '19-10-2024', 'After intense intellectual battles, the teams came to a decisive meeting, where every correct answer can be decisive!', 1, 1, 'Astana', '16:00:00', 'AITU - C1.1.334L'),
                    ('AITU Commencement Party', '11-08-2024', 'We are thrilled to invite you to AITU Commencement Party! It`s time to officially join our family and meet new friendse.', 4, 4, 'Astana', '16:00:00', 'West Hall'),
                    ('Club fair', '18-09-2024', 'AITU has a huge number of clubs. We know that freshmen can`t wait to learn more about each one and already start taking part in student life', 3, 3, 'Astana', '14:00:00', 'Assembly Hall'),
                    ('Отчетный концерт "Eurasia Band"', '22-11-2024', 'We invite Friends from AITU to attend the Eurasia Band reporting concert. Unforgettable impressions and a warm welcome await you!', 2,2, 'Astana', '17:00:00', 'Kazhymukan 11, edu&lab'),
                    ('СТУДЕНЧЕСКИЙ КИНОВЕЧЕР: Гарри Поттер и Кубок огня', '14-10-2024', 'Don`t miss the chance to immerse yourself in the world of magic and spend time with friends! Come and get a charge of positive emotions!', 4,4, 'Astana', '18:00:00', 'Assembly Hall'),
                    ('Music Spooktacular', '31-10-2024', 'Through the fog of an October night, when the world of the living and the dead almost touch, we invite you to the “Music Spooktacular”', 2,2, 'Astana', '17:00:00', 'Assembly Hall');
                    
            INSERT INTO Tickets(event_id,price)
            VALUES(1, 1000),
                  (2, 500),
                  (3, 200),
                  (4, 6000),
                  (5, 200),
                  (6, 1000),
                  (7, 1000),
                  (8, 1500);
        
            """)
            print("ok")
except psycopg2.Error as e:
    print(f"{e}")
