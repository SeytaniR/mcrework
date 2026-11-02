with open('web/main.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "  // ==========================================\n  // MODAIS DE CATALOGO (CLASSES & MONSTROS)\n  // =========================================="
end_marker = "  // Expor para debug e inspeção"

idx1 = text.find(start_marker)
idx2 = text.find(end_marker)

print("idx1:", idx1, "idx2:", idx2)
if idx1 != -1 and idx2 != -1:
    print("Block to replace length:", idx2 - idx1)
