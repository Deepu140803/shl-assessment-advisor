#!/usr/bin/env bash
# ============================================================
# setup.sh — One-shot setup for SHL Assessment Recommender
# Run: bash setup.sh
# ============================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║   SHL Assessment Recommender - Setup     ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 1: Check Python ──────────────────────────────────────
echo -e "${CYAN}[1/6] Checking Python version...${NC}"
python3 --version || { echo -e "${RED}Python 3.9+ required${NC}"; exit 1; }

# ── Step 2: Create virtualenv ────────────────────────────────
echo -e "${CYAN}[2/6] Creating Python virtual environment...${NC}"
cd backend
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# ── Step 3: Install Python deps ──────────────────────────────
echo -e "${CYAN}[3/6] Installing Python dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
cd ..

# ── Step 4: Copy .env files ──────────────────────────────────
echo -e "${CYAN}[4/6] Setting up environment files...${NC}"
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${YELLOW}  ⚠  Created .env from example. Please fill in your API keys!${NC}"
fi
if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  echo -e "${YELLOW}  ⚠  Created backend/.env from example.${NC}"
fi

# ── Step 5: Scrape/seed catalog ──────────────────────────────
echo -e "${CYAN}[5/6] Seeding SHL catalog (fallback mode)...${NC}"
mkdir -p data
cd backend
source venv/bin/activate 2>/dev/null || true
python ../scripts/scrape_catalog.py --fallback
cd ..

# ── Step 6: Install frontend deps ────────────────────────────
echo -e "${CYAN}[6/6] Installing frontend dependencies...${NC}"
cd frontend
npm install --silent
cd ..

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env and backend/.env with your API keys"
echo "  2. Generate embeddings: cd backend && python ../scripts/generate_embeddings.py"
echo "  3. Start backend:  cd backend && uvicorn app.main:app --reload"
echo "  4. Start frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker: docker-compose up --build"
echo ""
