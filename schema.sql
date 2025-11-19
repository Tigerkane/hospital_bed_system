CREATE DATABASE IF NOT EXISTS covid_beds CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE covid_beds;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  phone VARCHAR(30),
  password VARCHAR(255) NOT NULL,
  role ENUM('patient','hospital','admin') DEFAULT 'patient',
  hospital_id INT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hospitals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  city VARCHAR(100),
  contact VARCHAR(50),
  icu_total INT DEFAULT 0,
  oxygen_total INT DEFAULT 0,
  normal_total INT DEFAULT 0,
  ventilator_total INT DEFAULT 0,
  icu_available INT DEFAULT 0,
  oxygen_available INT DEFAULT 0,
  normal_available INT DEFAULT 0,
  ventilator_available INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  hospital_id INT NOT NULL,
  bed_type ENUM('icu','oxygen','normal','ventilator') NOT NULL,
  status ENUM('pending','confirmed','cancelled','discharged') DEFAULT 'pending',
  name VARCHAR(150),
  contact VARCHAR(50),
  symptoms TEXT,
  id_proof VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

CREATE TABLE waitlist (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  bed_type ENUM('icu','oxygen','normal','ventilator') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
);
