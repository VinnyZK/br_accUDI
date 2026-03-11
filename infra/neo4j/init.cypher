// ── OpenUDI Neo4j Schema ─────────────────────────
// Uniqueness constraints
CREATE CONSTRAINT person_cpf IF NOT EXISTS FOR (n:Person) REQUIRE n.cpf IS UNIQUE;
CREATE CONSTRAINT company_cnpj IF NOT EXISTS FOR (n:Company) REQUIRE n.cnpj IS UNIQUE;
CREATE CONSTRAINT contract_id IF NOT EXISTS FOR (n:Contract) REQUIRE n.contract_id IS UNIQUE;
CREATE CONSTRAINT sanction_id IF NOT EXISTS FOR (n:Sanction) REQUIRE n.sanction_id IS UNIQUE;
CREATE CONSTRAINT amendment_id IF NOT EXISTS FOR (n:Amendment) REQUIRE n.amendment_id IS UNIQUE;
CREATE CONSTRAINT public_office_id IF NOT EXISTS FOR (n:PublicOffice) REQUIRE n.office_id IS UNIQUE;
CREATE CONSTRAINT tax_debt_id IF NOT EXISTS FOR (n:TaxDebt) REQUIRE n.debt_id IS UNIQUE;
CREATE CONSTRAINT tax_waiver_id IF NOT EXISTS FOR (n:TaxWaiver) REQUIRE n.waiver_id IS UNIQUE;
CREATE CONSTRAINT cultural_incentive_id IF NOT EXISTS FOR (n:CulturalIncentive) REQUIRE n.incentive_id IS UNIQUE;
CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (n:Transfer) REQUIRE n.transfer_id IS UNIQUE;
CREATE CONSTRAINT partner_id IF NOT EXISTS FOR (n:Partner) REQUIRE n.partner_id IS UNIQUE;
CREATE CONSTRAINT ingestion_run_id IF NOT EXISTS FOR (n:IngestionRun) REQUIRE n.run_id IS UNIQUE;

// ── Indexes ─────────────────────────────────────
CREATE INDEX person_name IF NOT EXISTS FOR (n:Person) ON (n.name);
CREATE INDEX company_razao IF NOT EXISTS FOR (n:Company) ON (n.razao_social);
CREATE INDEX company_municipio IF NOT EXISTS FOR (n:Company) ON (n.municipio);
CREATE INDEX contract_value IF NOT EXISTS FOR (n:Contract) ON (n.value);
CREATE INDEX contract_date IF NOT EXISTS FOR (n:Contract) ON (n.date);
CREATE INDEX contract_org IF NOT EXISTS FOR (n:Contract) ON (n.contracting_org);

// ── Full-text search index ──────────────────────
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS
FOR (n:Person|Company|Contract|Sanction|Amendment|TaxDebt|TaxWaiver|CulturalIncentive|Transfer)
ON EACH [n.name, n.razao_social, n.cpf, n.cnpj, n.object, n.contracting_org];
