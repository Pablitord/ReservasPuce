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

-- Datos de ejemplo para espacios (opcional)
INSERT INTO spaces (name, type, capacity, description) VALUES
    ('Aula 101', 'aula', 40, 'Aula principal del primer piso'),
    ('Aula 102', 'aula', 35, 'Aula del primer piso'),
    ('Aula 201', 'aula', 50, 'Aula principal del segundo piso'),
    ('Laboratorio de Computación 1', 'laboratorio', 30, 'Laboratorio con 30 computadoras'),
    ('Laboratorio de Computación 2', 'laboratorio', 30, 'Laboratorio con 30 computadoras'),
    ('Laboratorio de Física', 'laboratorio', 25, 'Laboratorio equipado para prácticas de física'),
    ('Laboratorio de Química', 'laboratorio', 25, 'Laboratorio equipado para prácticas de química'),
    ('Auditorio Principal', 'auditorio', 200, 'Auditorio principal de la universidad'),
    ('Auditorio Menor', 'auditorio', 100, 'Auditorio para eventos pequeños')
ON CONFLICT DO NOTHING;

-- Crear un usuario administrador por defecto (cambiar la contraseña después)
-- Contraseña por defecto: admin123 (debe cambiarse en producción)
INSERT INTO users (email, password_hash, name, student_id, role) VALUES
    ('admin@puce.edu.ec', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5KqZz8eHGqR1q', 'Administrador', 'ADMIN001', 'admin')
ON CONFLICT (email) DO NOTHING;
