CREATE DATABASE IF NOT EXISTS bits_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bits_inventory;
-- Namespaced tables let this Python/C web edition coexist with the Java edition.
CREATE TABLE IF NOT EXISTS web_users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(190) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS web_categories (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 name VARCHAR(100) NOT NULL,
 UNIQUE KEY uq_web_category_user_name(user_id,name),
 CONSTRAINT fk_web_category_user FOREIGN KEY(user_id) REFERENCES web_users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS web_components (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 category_id INT NULL,
 name VARCHAR(150) NOT NULL,
 component_value VARCHAR(100) DEFAULT '',
 quantity INT NOT NULL DEFAULT 0,
 location VARCHAR(150) DEFAULT '',
 notes TEXT,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_web_components_user(user_id),
 CONSTRAINT fk_web_component_user FOREIGN KEY(user_id) REFERENCES web_users(id) ON DELETE CASCADE,
 CONSTRAINT fk_web_component_category FOREIGN KEY(category_id) REFERENCES web_categories(id) ON DELETE SET NULL,
 CONSTRAINT chk_web_component_quantity CHECK(quantity >= 0)
) ENGINE=InnoDB;
