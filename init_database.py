#!/usr/bin/env python3
"""
Script para inicializar o banco de dados PostgreSQL
Execute este script uma vez para criar todas as tabelas
"""
import asyncio
from src.database.db import db

async def main():
    print("🔧 Inicializando banco de dados...")
    print(f"📍 URL do banco: {db.engine.url}")
    
    try:
        await db.init_db()
        print("✅ Banco de dados inicializado com sucesso!")
        print("✅ Todas as tabelas foram criadas!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
