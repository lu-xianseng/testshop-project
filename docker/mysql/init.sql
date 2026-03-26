SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 预置数据
INSERT INTO products (name, price, stock) VALUES
('iPhone 15', 999.00, 100),
('MacBook Pro M3', 2499.00, 50),
('AirPods Pro 2', 199.00, 200),
('iPad Air', 599.00, 80);