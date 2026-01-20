-- Schema para el sistema de reservas PUCE

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de espacios
CREATE TABLE IF NOT EXISTS spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('aula', 'laboratorio', 'auditorio')),
    floor VARCHAR(20) NOT NULL DEFAULT 'planta_baja' CHECK (floor IN ('planta_baja', 'piso_1', 'piso_2')),
    capacity INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    space_id UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    justification TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_time_order CHECK (end_time > start_time)
);

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    link VARCHAR(500),
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_space_id ON reservations(space_id);
CREATE INDEX IF NOT EXISTS idx_reservations_date ON reservations(date);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_spaces_type ON spaces(type);
CREATE INDEX IF NOT EXISTS idx_spaces_floor ON spaces(floor);

-- Datos de ejemplo para espacios (opcional)
INSERT INTO spaces (name, type, floor, capacity, description) VALUES
    ('Aula 101', 'aula', 'piso_1', 40, 'Aula principal del primer piso'),
    ('Aula 102', 'aula', 'piso_1', 35, 'Aula del primer piso'),
    ('Aula 201', 'aula', 'piso_2', 50, 'Aula principal del segundo piso'),
    ('Laboratorio de Computación 1', 'laboratorio', 'planta_baja', 30, 'Laboratorio con 30 computadoras'),
    ('Laboratorio de Computación 2', 'laboratorio', 'planta_baja', 30, 'Laboratorio con 30 computadoras'),
    ('Laboratorio de Física', 'laboratorio', 'planta_baja', 25, 'Laboratorio equipado para prácticas de física'),
    ('Laboratorio de Química', 'laboratorio', 'planta_baja', 25, 'Laboratorio equipado para prácticas de química'),
    ('Auditorio Principal', 'auditorio', 'planta_baja', 200, 'Auditorio principal de la universidad'),
    ('Auditorio Menor', 'auditorio', 'planta_baja', 100, 'Auditorio para eventos pequeños')
ON CONFLICT DO NOTHING;

-- Salones A-### (insertar solo si no existen)
INSERT INTO spaces (name, type, floor, capacity, description)
SELECT v.name, v.type, v.floor, v.capacity, v.description
FROM (VALUES
    ('A-001', 'aula', 'planta_baja', 30, 'Enfermería - Anatomía y Morfofunción'),
    ('A-002', 'laboratorio', 'planta_baja', 30, 'Laboratorio de Informática'),
    ('A-003', 'laboratorio', 'planta_baja', 30, 'Laboratorio CBS IV - Microbiología'),
    ('A-004', 'laboratorio', 'planta_baja', 30, 'Laboratorio CBS III - Inmunohematología / Genética'),
    ('A-005', 'aula', 'planta_baja', 30, 'Ingeniería en Alimentos'),
    ('A-006', 'laboratorio', 'planta_baja', 30, 'Laboratorio - Histología / Histopatología'),
    ('A-008', 'laboratorio', 'planta_baja', 30, 'Sala de Simulación de Audiencias'),
    ('A-009', 'aula', 'planta_baja', 30, 'Biología Marina'),
    ('A-010', 'laboratorio', 'planta_baja', 30, 'Laboratorio de Simulación - Semiología'),
    ('A-011', 'laboratorio', 'planta_baja', 30, 'Laboratorio de Simulación - Clínica y Destrezas'),
    ('A-013', 'laboratorio', 'planta_baja', 30, 'Laboratorio de Morfofunción'),
    ('A-014', 'laboratorio', 'planta_baja', 30, 'Laboratorio de Simulación'),
    ('A-101', 'aula', 'piso_1', 30, 'Espacio A-101'),
    ('A-102', 'aula', 'piso_1', 30, 'Espacio A-102'),
    ('A-103', 'aula', 'piso_1', 30, 'Espacio A-103'),
    ('A-104', 'aula', 'piso_1', 30, 'Espacio A-104'),
    ('A-105', 'aula', 'piso_1', 30, 'Espacio A-105'),
    ('A-106', 'aula', 'piso_1', 30, 'Espacio A-106'),
    ('A-109', 'aula', 'piso_1', 30, 'Espacio A-109'),
    ('A-110', 'aula', 'piso_1', 30, 'Espacio A-110'),
    ('A-111', 'aula', 'piso_1', 30, 'Espacio A-111'),
    ('A-112', 'aula', 'piso_1', 30, 'Espacio A-112'),
    ('A-113', 'aula', 'piso_1', 30, 'Espacio A-113'),
    ('A-114', 'aula', 'piso_1', 30, 'Espacio A-114'),
    ('A-201', 'aula', 'piso_2', 30, 'Espacio A-201'),
    ('A-202', 'aula', 'piso_2', 30, 'Espacio A-202'),
    ('A-203', 'aula', 'piso_2', 30, 'Espacio A-203'),
    ('A-204', 'aula', 'piso_2', 30, 'Espacio A-204'),
    ('A-205', 'aula', 'piso_2', 30, 'Espacio A-205'),
    ('A-206', 'aula', 'piso_2', 30, 'Espacio A-206'),
    ('A-207', 'aula', 'piso_2', 30, 'Espacio A-207'),
    ('A-208', 'aula', 'piso_2', 30, 'Espacio A-208'),
    ('A-209', 'aula', 'piso_2', 30, 'Espacio A-209'),
    ('A-210', 'aula', 'piso_2', 30, 'Espacio A-210'),
    ('A-211', 'aula', 'piso_2', 30, 'Espacio A-211'),
    ('A-212', 'aula', 'piso_2', 30, 'Espacio A-212'),
    ('A-213', 'aula', 'piso_2', 30, 'Espacio A-213')
) AS v(name, type, floor, capacity, description)
WHERE NOT EXISTS (
    SELECT 1 FROM spaces s WHERE s.name = v.name
);

-- Ajustar piso de aulas según el prefijo A-0/A-1/A-2
UPDATE spaces
SET floor = CASE
    WHEN name LIKE 'A-0%' THEN 'planta_baja'
    WHEN name LIKE 'A-1%' THEN 'piso_1'
    WHEN name LIKE 'A-2%' THEN 'piso_2'
    ELSE floor
END;

-- Auditorios en planta baja
UPDATE spaces
SET floor = 'planta_baja'
WHERE name ILIKE 'Auditorio%';

-- Crear un usuario administrador por defecto (cambiar la contraseña después)
-- Contraseña por defecto: admin123 (debe cambiarse en producción)
INSERT INTO users (email, password_hash, name, student_id, role) VALUES
    ('admin@puce.edu.ec', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5KqZz8eHGqR1q', 'Administrador', 'ADMIN001', 'admin')
ON CONFLICT (email) DO NOTHING;
