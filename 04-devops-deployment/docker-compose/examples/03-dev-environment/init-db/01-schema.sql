-- Development database initialization

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sample data
INSERT INTO items (name, description) VALUES
    ('Item 1', 'First test item'),
    ('Item 2', 'Second test item'),
    ('Item 3', 'Third test item')
ON CONFLICT DO NOTHING;
