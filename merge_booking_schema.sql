BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS travel_app_userprofile (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    phone varchar(20) NOT NULL,
    avatar varchar(100) NULL,
    avatar_url varchar(500) NOT NULL,
    preferred_currency varchar(3) NOT NULL,
    bio text NOT NULL,
    updated_at datetime NOT NULL,
    user_id integer NOT NULL UNIQUE REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS travel_app_travelpackage (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    slug varchar(120) NOT NULL UNIQUE,
    name varchar(200) NOT NULL,
    destination varchar(100) NOT NULL,
    price varchar(50) NOT NULL,
    image_url varchar(600) NOT NULL,
    fallback_image varchar(200) NOT NULL,
    duration varchar(50) NOT NULL,
    hotel varchar(120) NOT NULL,
    transport varchar(120) NOT NULL,
    meal varchar(160) NOT NULL,
    highlights text NOT NULL,
    rating smallint unsigned NOT NULL CHECK (rating >= 0),
    reviews integer unsigned NOT NULL CHECK (reviews >= 0),
    is_featured bool NOT NULL,
    is_active bool NOT NULL,
    display_order integer unsigned NOT NULL CHECK (display_order >= 0),
    created_at datetime NOT NULL,
    updated_at datetime NOT NULL
);

CREATE TABLE IF NOT EXISTS travel_app_travelbooking (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    package_id varchar(100) NOT NULL,
    package_name varchar(200) NOT NULL,
    destination varchar(100) NOT NULL,
    price varchar(50) NOT NULL,
    duration varchar(50) NOT NULL,
    hotel varchar(120) NOT NULL,
    transport varchar(120) NOT NULL,
    meal varchar(160) NOT NULL,
    image_url varchar(600) NOT NULL,
    travelers integer unsigned NOT NULL CHECK (travelers >= 0),
    start_date date NULL,
    contact_phone varchar(20) NOT NULL,
    note text NOT NULL,
    status varchar(20) NOT NULL,
    booked_at datetime NOT NULL,
    user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS travel_app_travelbooking_user_id_idx ON travel_app_travelbooking(user_id);

CREATE TABLE IF NOT EXISTS travel_app_emailverificationcode (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    email varchar(254) NOT NULL,
    code varchar(6) NOT NULL,
    purpose varchar(30) NOT NULL,
    is_used bool NOT NULL,
    created_at datetime NOT NULL,
    expires_at datetime NOT NULL
);

CREATE INDEX IF NOT EXISTS travel_app_emailverificationcode_email_idx ON travel_app_emailverificationcode(email);

INSERT INTO django_migrations (app, name, applied)
SELECT 'travel_app', '0005_userprofile_travelpackage_travelbooking_emailcode', datetime('now')
WHERE NOT EXISTS (
    SELECT 1 FROM django_migrations
    WHERE app = 'travel_app'
      AND name = '0005_userprofile_travelpackage_travelbooking_emailcode'
);

COMMIT;
