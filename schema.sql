DROP TABLE IF EXISTS cat;

CREATE TABLE cat (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    personality VARCHAR(255) NOT NULL,
    appearance VARCHAR(255) NOT NULL,
    power_level INTEGER NOT NULL,
    description VARCHAR(255) NOT NULL,
    image_path TEXT NOT NULL,
    latest_adoption_id INTEGER,
    FOREIGN KEY (latest_adoption_id) REFERENCES Adoption(id)
);

INSERT INTO cat (id, name, personality, appearance, power_level, description, image_path) VALUES
  (108, 'Tubbs', 'Finicky Feaster', 'Fluffy', 130, 'BIG ol cat but placeholder', 'Images/tubbs.png'),
  (104, 'Saint Purrtrick', 'Awe-inspiring', 'Ethereal', 222, 'Awe-inspiring placeholder bro', 'Images/saint_purrtrick.png'),
  (107, 'Conductor Whiskers', 'Vigilant', 'Railway Uniform', 50, 'CUTIE placeholder', 'Images/conductor_whiskers.png'),
  (105, 'Ms. Fortune', 'Charismatic', 'Gold', 20, 'Waving placeholder', 'Images/ms_fortune.png'),
  (114, 'Sassy Fran', 'Enthusiastic', 'Waitress', 180, 'Classy placeholder', 'Images/sassy_fran.png'),
  (102, 'Xerxes IX', 'Regal', 'Persian', 70, 'Regal placeholder', 'Images/xerxes_ix.png'),
  (106, 'Bob the Cat', 'Outdoorsy', 'Adventurer', 40, 'Adventurer placeholder', 'Images/bob_the_cat.png'),
  (101, 'Senor Don Gato', 'Scheming', 'Fisherman', 30, 'Scheming placeholder', 'Images/senor_don_gato.png'),
  (109, 'Mr. Meowgi', 'Mentoring', 'Ronin', 250, 'Mentor placeholder', 'Images/mr_meowgi.png'),
  (103, 'Chairman Meow', 'Boorish', 'Camouflage', 111, 'Boorish placeholder', 'Images/chairman_meow.png'),
  (110, 'Lady Meow-Meow', 'Diva', 'American Shorthair', 100, 'Diva placeholder', 'Images/lady_meow_meow.png'),
  (111, 'Guy Furry', 'Artisan', 'Apron', 30, 'Artisan placeholder', 'Images/guy_furry.png'),
  (112, 'Kathmandu', 'Refined', 'Hunting Coat', 150, 'Refined placeholder', 'Images/kathmandu.png'),
  (113, 'Ramses the Great', 'Riddler', 'Sphinx', 230, 'Riddler placeholder', 'Images/ramses_the_great.png'),
  (115, 'Billy the Kitten', 'Nihilistic', 'Western Wear', 250, 'Nihilistic placeholder', 'Images/billy_the_kitten.png'),
  (116, 'Frosty', 'Sensitive', 'Straw Coat', 5, 'Sensitive placeholder', 'Images/frosty.png');

DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS adoption;

CREATE TABLE adoption (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    previous_owner_id INTEGER,
    cat_id INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    method TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (previous_owner_id) REFERENCES User(id),
    FOREIGN KEY (cat_id) REFERENCES Cat(id)
);