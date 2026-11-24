CREATE TABLE IF NOT EXISTS siswa (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    kelas VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT
CURRENT_TIMESTAMP
);

INSERT INTO siswa (nama, kelas)
VALUES
('Selvy Deffya', '5A'),
('Althaf Danes', '5A'),
('Almahira Aqeela', '5A'),
('Wening', '5A');
