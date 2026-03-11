// ── OpenUDI Synthetic Seed Data ──────────────────
// All data is fictional. CPFs/CNPJs are invalid test values.
// Exercises all 7 detection patterns for development.

// ── Persons (fictional politicians + family) ────
MERGE (p1:Person {cpf: '11111111111'}) SET p1.name = 'CARLOS SILVA NETO', p1.is_pep = true, p1.cargo = 'Vereador', p1.municipio = 'UBERLANDIA', p1.uf = 'MG', p1.patrimonio_declarado = 350000.00;
MERGE (p2:Person {cpf: '22222222222'}) SET p2.name = 'MARIA SILVA COSTA', p2.is_pep = false, p2.municipio = 'UBERLANDIA', p2.uf = 'MG';
MERGE (p3:Person {cpf: '33333333333'}) SET p3.name = 'JOAO OLIVEIRA SANTOS', p3.is_pep = true, p3.cargo = 'Prefeito', p3.municipio = 'UBERLANDIA', p3.uf = 'MG', p3.patrimonio_declarado = 1200000.00;
MERGE (p4:Person {cpf: '44444444444'}) SET p4.name = 'ANA OLIVEIRA LIMA', p4.is_pep = false, p4.municipio = 'UBERLANDIA', p4.uf = 'MG';
MERGE (p5:Person {cpf: '55555555555'}) SET p5.name = 'PEDRO MENDES JUNIOR', p5.is_pep = true, p5.cargo = 'Vereador', p5.municipio = 'UBERLANDIA', p5.uf = 'MG', p5.patrimonio_declarado = 180000.00;

// ── Family relationships ────────────────────────
MERGE (p1)-[:CONJUGE_DE]->(p2);
MERGE (p3)-[:CONJUGE_DE]->(p4);
MERGE (p1)-[:PARENTE_DE {grau: 'irmao'}]->(p5);

// ── Companies (fictional, Uberlândia) ───────────
MERGE (c1:Company {cnpj: '11111111000100'}) SET c1.razao_social = 'SILVA CONSTRUCOES LTDA', c1.cnae_principal = '4120400', c1.capital_social = 500000.00, c1.municipio = 'UBERLANDIA', c1.uf = 'MG', c1.situacao = 'ATIVA';
MERGE (c2:Company {cnpj: '22222222000100'}) SET c2.razao_social = 'OLIVEIRA SERVICOS SA', c2.cnae_principal = '8121400', c2.capital_social = 200000.00, c2.municipio = 'UBERLANDIA', c2.uf = 'MG', c2.situacao = 'ATIVA';
MERGE (c3:Company {cnpj: '33333333000100'}) SET c3.razao_social = 'TECH SOLUTIONS UDI LTDA', c3.cnae_principal = '6201501', c3.capital_social = 100000.00, c3.municipio = 'UBERLANDIA', c3.uf = 'MG', c3.situacao = 'ATIVA';
MERGE (c4:Company {cnpj: '44444444000100'}) SET c4.razao_social = 'MENDES TRANSPORTES LTDA', c4.cnae_principal = '4930202', c4.capital_social = 300000.00, c4.municipio = 'UBERLANDIA', c4.uf = 'MG', c4.situacao = 'ATIVA';
MERGE (c5:Company {cnpj: '55555555000100'}) SET c5.razao_social = 'COSTA ALIMENTOS EIRELI', c5.cnae_principal = '5611201', c5.capital_social = 80000.00, c5.municipio = 'UBERLANDIA', c5.uf = 'MG', c5.situacao = 'ATIVA';

// ── Partnerships (spouse/family own companies) ──
MERGE (p2)-[:SOCIO_DE {qualificacao: 'Socio-Administrador', data_entrada: '2018-03-15'}]->(c1);
MERGE (p4)-[:SOCIO_DE {qualificacao: 'Socio-Administrador', data_entrada: '2019-06-20'}]->(c2);
MERGE (p5)-[:SOCIO_DE {qualificacao: 'Socio', data_entrada: '2020-01-10'}]->(c4);
MERGE (p1)-[:SOCIO_DE {qualificacao: 'Socio', data_entrada: '2017-08-01'}]->(c3);

// ── Contracts (municipal) ───────────────────────
MERGE (ct1:Contract {contract_id: 'CTR-UDI-001'}) SET ct1.object = 'Reforma de escola municipal', ct1.value = 450000.00, ct1.contracting_org = 'Secretaria de Educacao', ct1.date = '2025-03-15', ct1.municipio = 'UBERLANDIA', ct1.modalidade = 'Pregao Eletronico';
MERGE (ct2:Contract {contract_id: 'CTR-UDI-002'}) SET ct2.object = 'Servico de limpeza urbana', ct2.value = 780000.00, ct2.contracting_org = 'Secretaria de Obras', ct2.date = '2025-05-20', ct2.municipio = 'UBERLANDIA', ct2.modalidade = 'Concorrencia';
MERGE (ct3:Contract {contract_id: 'CTR-UDI-003'}) SET ct3.object = 'Fornecimento de software', ct3.value = 65000.00, ct3.contracting_org = 'Prodaub', ct3.date = '2025-06-10', ct3.municipio = 'UBERLANDIA', ct3.modalidade = 'Dispensa';
MERGE (ct4:Contract {contract_id: 'CTR-UDI-004'}) SET ct4.object = 'Transporte escolar', ct4.value = 320000.00, ct4.contracting_org = 'Secretaria de Educacao', ct4.date = '2025-07-01', ct4.municipio = 'UBERLANDIA', ct4.modalidade = 'Pregao Eletronico';
MERGE (ct5:Contract {contract_id: 'CTR-UDI-005'}) SET ct5.object = 'Fornecimento de merenda', ct5.value = 75000.00, ct5.contracting_org = 'Secretaria de Educacao', ct5.date = '2025-07-15', ct5.municipio = 'UBERLANDIA', ct5.modalidade = 'Dispensa';

// ── Split contracts pattern (3x < R$80k same org/month)
MERGE (ct6:Contract {contract_id: 'CTR-UDI-006'}) SET ct6.object = 'Material de escritorio lote 1', ct6.value = 72000.00, ct6.contracting_org = 'Secretaria de Administracao', ct6.date = '2025-08-05', ct6.municipio = 'UBERLANDIA', ct6.modalidade = 'Dispensa';
MERGE (ct7:Contract {contract_id: 'CTR-UDI-007'}) SET ct7.object = 'Material de escritorio lote 2', ct7.value = 68000.00, ct7.contracting_org = 'Secretaria de Administracao', ct7.date = '2025-08-12', ct7.municipio = 'UBERLANDIA', ct7.modalidade = 'Dispensa';
MERGE (ct8:Contract {contract_id: 'CTR-UDI-008'}) SET ct8.object = 'Material de escritorio lote 3', ct8.value = 71000.00, ct8.contracting_org = 'Secretaria de Administracao', ct8.date = '2025-08-18', ct8.municipio = 'UBERLANDIA', ct8.modalidade = 'Dispensa';

// ── Contract wins ───────────────────────────────
MERGE (c1)-[:VENCEU]->(ct1);
MERGE (c2)-[:VENCEU]->(ct2);
MERGE (c3)-[:VENCEU]->(ct3);
MERGE (c4)-[:VENCEU]->(ct4);
MERGE (c5)-[:VENCEU]->(ct5);
MERGE (c3)-[:VENCEU]->(ct6);
MERGE (c3)-[:VENCEU]->(ct7);
MERGE (c3)-[:VENCEU]->(ct8);

// ── Sanction ────────────────────────────────────
MERGE (s1:Sanction {sanction_id: 'CEIS-UDI-001'}) SET s1.type = 'CEIS', s1.reason = 'Fraude em licitacao', s1.date_start = '2024-01-15', s1.date_end = '2027-01-15', s1.source = 'CGU';
MERGE (c2)-[:SANCIONADA]->(s1);

// ── Tax debt (municipal) ────────────────────────
MERGE (d1:TaxDebt {debt_id: 'DA-UDI-001'}) SET d1.tipo_divida = 'ISS', d1.valor_base = 125000.00, d1.valor_atualizado = 148000.00, d1.ano_vencimento = 2023;
MERGE (c4)-[:DEVEDOR]->(d1);

// ── Tax waiver (IPTU exemption) ─────────────────
MERGE (w1:TaxWaiver {waiver_id: 'REN-UDI-001'}) SET w1.tipo = 'Isencao IPTU', w1.legislacao = 'Lei 12345/2020', w1.ano = 2024, w1.valor_renunciado = 45000.00;
MERGE (c1)-[:BENEFICIARIO_ISENCAO]->(w1);

// ── Amendment ───────────────────────────────────
MERGE (a1:Amendment {amendment_id: 'EMD-UDI-001'}) SET a1.type = 'Individual', a1.function = 'Educacao', a1.value_committed = 500000.00, a1.value_paid = 350000.00, a1.year = 2025;
MERGE (p1)-[:AUTOR_EMENDA]->(a1);
MERGE (c1)-[:RECEBEU_EMENDA]->(a1);

// ── Elections ───────────────────────────────────
MERGE (e1:PublicOffice {office_id: 'ELEC-UDI-2024-001'}) SET e1.year = 2024, e1.cargo = 'Vereador', e1.municipio = 'UBERLANDIA', e1.uf = 'MG', e1.situacao = 'Eleito';
MERGE (p1)-[:CANDIDATO]->(e1);

// ── Campaign donation (donation-contract loop) ──
MERGE (c3)-[:DOOU_PARA {valor: 50000.00, ano: 2024}]->(e1);

// ── Cultural incentive ──────────────────────────
MERGE (ci1:CulturalIncentive {incentive_id: 'CULT-UDI-001'}) SET ci1.projeto = 'Festival Cultural do Triangulo', ci1.area = 'Musica', ci1.valor_aprovado = 200000.00, ci1.valor_captado = 180000.00, ci1.ano = 2025, ci1.status = 'Realizado';
MERGE (p5)-[:PROPONENTE]->(ci1);
MERGE (c4)-[:INCENTIVADORA {valor: 80000.00, incentivo: 'ISS'}]->(ci1);

// ── Transfer ────────────────────────────────────
MERGE (t1:Transfer {transfer_id: 'TRANSF-UDI-001'}) SET t1.tipo = 'Fundo a Fundo', t1.valor = 2500000.00, t1.programa = 'PAB Fixo', t1.ano = 2025, t1.orgao_superior = 'Ministerio da Saude';

// ── Patterns exercised ──────────────────────────
// 1. Sancionada com contrato: c2 SANCIONADA + VENCEU ct2
// 2. Fracionamento: c3 VENCEU ct6+ct7+ct8 (mesmo mes, < R$80k)
// 3. Doador->contrato: c3 DOOU_PARA p1 + VENCEU ct3/ct6/ct7/ct8
// 4. Parente com contrato: p1 (vereador) CONJUGE p2 (socia c1) + c1 VENCEU ct1
// 5. Isencao + contrato: c1 BENEFICIARIO_ISENCAO + VENCEU ct1
// 6. Devedor com contrato: c4 DEVEDOR + VENCEU ct4
// 7. Incentivo cultural cruzado: p5 (vereador/irmao p1) PROPONENTE + c4 INCENTIVADORA
