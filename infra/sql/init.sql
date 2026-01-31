-- Enable UUID generation helper
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Orders table (captures order requests)
CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT,
  product_id TEXT,
  amount NUMERIC(12,2),
  status TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Payments table (stores the outcome of payment process)
CREATE TABLE IF NOT EXISTS payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(id),
  status TEXT,        -- e.g., SUCCESS / FAILED
  txn_ref TEXT,       -- some fake ref
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Inventory table (stock levels per product)
CREATE TABLE IF NOT EXISTS inventory (
  product_id TEXT PRIMARY KEY,
  quantity INT
);

-- Event log (optional, for auditing/replay/debug)
CREATE TABLE IF NOT EXISTS event_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type TEXT,
  key TEXT,
  payload_json JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed: we start with a couple of products
INSERT INTO inventory(product_id, quantity) VALUES
  ('p-42', 100),
  ('p-43', 50)
ON CONFLICT (product_id) DO NOTHING;