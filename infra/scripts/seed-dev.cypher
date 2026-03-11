// ── OpenUDI Synthetic Seed Data ──────────────────
// All data is fictional. CPFs/CNPJs are invalid test values.
// Uses MATCH for relationships since cypher-shell runs statements independently.

// ── Persons ─────────────────────────────────────
MERGE (n:Person {cpf: '11111111111'}) SET n.name = 'CARLOS SILVA NETO', n.is_pep = true, n.cargo = 'Vereador', n.municipio = 'UBERLANDIA', n.uf = 'MG', n.patrimonio_declarado = 350000.00;
MERGE (n:Person {cpf: '22222222222'}) SET n.name = 'MARIA SILVA COSTA', n.is_pep = false, n.municipio = 'UBERLANDIA', n.uf = 'MG';
MERGE (n:Person {cpf: '33333333333'}) SET n.name = 'JOAO OLIVEIRA SANTOS', n.is_pep = true, n.cargo = 'Prefeito', n.municipio = 'UBERLANDIA', n.uf = 'MG', n.patrimonio_declarado = 1200000.00;
MERGE (n:Person {cpf: '44444444444'}) SET n.name = 'ANA OLIVEIRA LIMA', n.is_pep = false, n.municipio = 'UBERLANDIA', n.uf = 'MG';
MERGE (n:Person {cpf: '55555555555'}) SET n.name = 'PEDRO MENDES JUNIOR', n.is_pep = true, n.cargo = 'Vereador', n.municipio = 'UBERLANDIA', n.uf = 'MG', n.patrimonio_declarado = 180000.00;

// ── Companies ───────────────────────────────────
MERGE (n:Company {cnpj: '11111111000100'}) SET n.razao_social = 'SILVA CONSTRUCOES LTDA', n.cnae_principal = '4120400', n.capital_social = 500000.00, n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'ATIVA';
MERGE (n:Company {cnpj: '22222222000100'}) SET n.razao_social = 'OLIVEIRA SERVICOS SA', n.cnae_principal = '8121400', n.capital_social = 200000.00, n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'ATIVA';
MERGE (n:Company {cnpj: '33333333000100'}) SET n.razao_social = 'TECH SOLUTIONS UDI LTDA', n.cnae_principal = '6201501', n.capital_social = 100000.00, n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'ATIVA';
MERGE (n:Company {cnpj: '44444444000100'}) SET n.razao_social = 'MENDES TRANSPORTES LTDA', n.cnae_principal = '4930202', n.capital_social = 300000.00, n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'ATIVA';
MERGE (n:Company {cnpj: '55555555000100'}) SET n.razao_social = 'COSTA ALIMENTOS EIRELI', n.cnae_principal = '5611201', n.capital_social = 80000.00, n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'ATIVA';

// ── Contracts ───────────────────────────────────
MERGE (n:Contract {contract_id: 'CTR-UDI-001'}) SET n.object = 'Reforma de escola municipal', n.value = 450000.00, n.contracting_org = 'Secretaria de Educacao', n.date = '2025-03-15', n.municipio = 'UBERLANDIA', n.modalidade = 'Pregao Eletronico';
MERGE (n:Contract {contract_id: 'CTR-UDI-002'}) SET n.object = 'Servico de limpeza urbana', n.value = 780000.00, n.contracting_org = 'Secretaria de Obras', n.date = '2025-05-20', n.municipio = 'UBERLANDIA', n.modalidade = 'Concorrencia';
MERGE (n:Contract {contract_id: 'CTR-UDI-003'}) SET n.object = 'Fornecimento de software', n.value = 65000.00, n.contracting_org = 'Prodaub', n.date = '2025-06-10', n.municipio = 'UBERLANDIA', n.modalidade = 'Dispensa';
MERGE (n:Contract {contract_id: 'CTR-UDI-004'}) SET n.object = 'Transporte escolar', n.value = 320000.00, n.contracting_org = 'Secretaria de Educacao', n.date = '2025-07-01', n.municipio = 'UBERLANDIA', n.modalidade = 'Pregao Eletronico';
MERGE (n:Contract {contract_id: 'CTR-UDI-005'}) SET n.object = 'Fornecimento de merenda', n.value = 75000.00, n.contracting_org = 'Secretaria de Educacao', n.date = '2025-07-15', n.municipio = 'UBERLANDIA', n.modalidade = 'Dispensa';
MERGE (n:Contract {contract_id: 'CTR-UDI-006'}) SET n.object = 'Material de escritorio lote 1', n.value = 72000.00, n.contracting_org = 'Secretaria de Administracao', n.date = '2025-08-05', n.municipio = 'UBERLANDIA', n.modalidade = 'Dispensa';
MERGE (n:Contract {contract_id: 'CTR-UDI-007'}) SET n.object = 'Material de escritorio lote 2', n.value = 68000.00, n.contracting_org = 'Secretaria de Administracao', n.date = '2025-08-12', n.municipio = 'UBERLANDIA', n.modalidade = 'Dispensa';
MERGE (n:Contract {contract_id: 'CTR-UDI-008'}) SET n.object = 'Material de escritorio lote 3', n.value = 71000.00, n.contracting_org = 'Secretaria de Administracao', n.date = '2025-08-18', n.municipio = 'UBERLANDIA', n.modalidade = 'Dispensa';

// ── Other entities ──────────────────────────────
MERGE (n:Sanction {sanction_id: 'CEIS-UDI-001'}) SET n.type = 'CEIS', n.reason = 'Fraude em licitacao', n.date_start = '2024-01-15', n.date_end = '2027-01-15', n.source = 'CGU';
MERGE (n:TaxDebt {debt_id: 'DA-UDI-001'}) SET n.tipo_divida = 'ISS', n.valor_base = 125000.00, n.valor_atualizado = 148000.00, n.ano_vencimento = 2023;
MERGE (n:TaxWaiver {waiver_id: 'REN-UDI-001'}) SET n.tipo = 'Isencao IPTU', n.legislacao = 'Lei 12345/2020', n.ano = 2024, n.valor_renunciado = 45000.00;
MERGE (n:Amendment {amendment_id: 'EMD-UDI-001'}) SET n.type = 'Individual', n.function = 'Educacao', n.value_committed = 500000.00, n.value_paid = 350000.00, n.year = 2025;
MERGE (n:PublicOffice {office_id: 'ELEC-UDI-2024-001'}) SET n.year = 2024, n.cargo = 'Vereador', n.municipio = 'UBERLANDIA', n.uf = 'MG', n.situacao = 'Eleito';
MERGE (n:CulturalIncentive {incentive_id: 'CULT-UDI-001'}) SET n.projeto = 'Festival Cultural do Triangulo', n.area = 'Musica', n.valor_aprovado = 200000.00, n.valor_captado = 180000.00, n.ano = 2025, n.status = 'Realizado';
MERGE (n:Transfer {transfer_id: 'TRANSF-UDI-001'}) SET n.tipo = 'Fundo a Fundo', n.valor = 2500000.00, n.programa = 'PAB Fixo', n.ano = 2025, n.orgao_superior = 'Ministerio da Saude';

// ── Family relationships ────────────────────────
MATCH (a:Person {cpf: '11111111111'}), (b:Person {cpf: '22222222222'}) MERGE (a)-[:CONJUGE_DE]->(b);
MATCH (a:Person {cpf: '33333333333'}), (b:Person {cpf: '44444444444'}) MERGE (a)-[:CONJUGE_DE]->(b);
MATCH (a:Person {cpf: '11111111111'}), (b:Person {cpf: '55555555555'}) MERGE (a)-[:PARENTE_DE {grau: 'irmao'}]->(b);

// ── Partnerships ────────────────────────────────
MATCH (a:Person {cpf: '22222222222'}), (b:Company {cnpj: '11111111000100'}) MERGE (a)-[:SOCIO_DE {qualificacao: 'Socio-Administrador', data_entrada: '2018-03-15'}]->(b);
MATCH (a:Person {cpf: '44444444444'}), (b:Company {cnpj: '22222222000100'}) MERGE (a)-[:SOCIO_DE {qualificacao: 'Socio-Administrador', data_entrada: '2019-06-20'}]->(b);
MATCH (a:Person {cpf: '55555555555'}), (b:Company {cnpj: '44444444000100'}) MERGE (a)-[:SOCIO_DE {qualificacao: 'Socio', data_entrada: '2020-01-10'}]->(b);
MATCH (a:Person {cpf: '11111111111'}), (b:Company {cnpj: '33333333000100'}) MERGE (a)-[:SOCIO_DE {qualificacao: 'Socio', data_entrada: '2017-08-01'}]->(b);

// ── Contract wins ───────────────────────────────
MATCH (a:Company {cnpj: '11111111000100'}), (b:Contract {contract_id: 'CTR-UDI-001'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '22222222000100'}), (b:Contract {contract_id: 'CTR-UDI-002'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '33333333000100'}), (b:Contract {contract_id: 'CTR-UDI-003'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '44444444000100'}), (b:Contract {contract_id: 'CTR-UDI-004'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '55555555000100'}), (b:Contract {contract_id: 'CTR-UDI-005'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '33333333000100'}), (b:Contract {contract_id: 'CTR-UDI-006'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '33333333000100'}), (b:Contract {contract_id: 'CTR-UDI-007'}) MERGE (a)-[:VENCEU]->(b);
MATCH (a:Company {cnpj: '33333333000100'}), (b:Contract {contract_id: 'CTR-UDI-008'}) MERGE (a)-[:VENCEU]->(b);

// ── Sanction relationship ───────────────────────
MATCH (a:Company {cnpj: '22222222000100'}), (b:Sanction {sanction_id: 'CEIS-UDI-001'}) MERGE (a)-[:SANCIONADA]->(b);

// ── Tax debt relationship ───────────────────────
MATCH (a:Company {cnpj: '44444444000100'}), (b:TaxDebt {debt_id: 'DA-UDI-001'}) MERGE (a)-[:DEVEDOR]->(b);

// ── Tax waiver relationship ─────────────────────
MATCH (a:Company {cnpj: '11111111000100'}), (b:TaxWaiver {waiver_id: 'REN-UDI-001'}) MERGE (a)-[:BENEFICIARIO_ISENCAO]->(b);

// ── Amendment relationships ─────────────────────
MATCH (a:Person {cpf: '11111111111'}), (b:Amendment {amendment_id: 'EMD-UDI-001'}) MERGE (a)-[:AUTOR_EMENDA]->(b);
MATCH (a:Company {cnpj: '11111111000100'}), (b:Amendment {amendment_id: 'EMD-UDI-001'}) MERGE (a)-[:RECEBEU_EMENDA]->(b);

// ── Election + donation ─────────────────────────
MATCH (a:Person {cpf: '11111111111'}), (b:PublicOffice {office_id: 'ELEC-UDI-2024-001'}) MERGE (a)-[:CANDIDATO]->(b);
MATCH (a:Company {cnpj: '33333333000100'}), (b:PublicOffice {office_id: 'ELEC-UDI-2024-001'}) MERGE (a)-[:DOOU_PARA {valor: 50000.00, ano: 2024}]->(b);

// ── Cultural incentive relationships ────────────
MATCH (a:Person {cpf: '55555555555'}), (b:CulturalIncentive {incentive_id: 'CULT-UDI-001'}) MERGE (a)-[:PROPONENTE]->(b);
MATCH (a:Company {cnpj: '44444444000100'}), (b:CulturalIncentive {incentive_id: 'CULT-UDI-001'}) MERGE (a)-[:INCENTIVADORA {valor: 80000.00, incentivo: 'ISS'}]->(b);

// ── Patterns exercised ──────────────────────────
// 1. Sancionada com contrato: OLIVEIRA SERVICOS (SANCIONADA) + VENCEU CTR-002
// 2. Fracionamento: TECH SOLUTIONS VENCEU CTR-006+007+008 (mesmo mes, < R$80k)
// 3. Doador->contrato: TECH SOLUTIONS DOOU_PARA vereador + VENCEU contratos
// 4. Parente com contrato: CARLOS (vereador) CONJUGE MARIA (socia SILVA CONSTRUCOES) + VENCEU CTR-001
// 5. Isencao + contrato: SILVA CONSTRUCOES BENEFICIARIO_ISENCAO + VENCEU CTR-001
// 6. Devedor com contrato: MENDES TRANSPORTES DEVEDOR + VENCEU CTR-004
// 7. Incentivo cultural cruzado: PEDRO (vereador) PROPONENTE + MENDES TRANSPORTES INCENTIVADORA
