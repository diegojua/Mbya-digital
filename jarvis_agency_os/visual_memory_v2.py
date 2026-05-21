"""
Visual Memory v2 — Persistência com SQLite + Versionamento + Cleanup Automático
Substitui o JSON por banco de dados estruturado com melhor performance e confiabilidade.
"""
import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory")
DB_FILE = os.path.join(MEMORY_DIR, "visual_memory.db")
BACKUP_DIR = os.path.join(MEMORY_DIR, "backups")


def _ensure_dirs():
    """Garante existência de diretórios."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def _init_database():
    """Inicializa schema do banco de dados."""
    _ensure_dirs()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabela principal de campanhas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT NOT NULL,
            niche TEXT,
            objective TEXT,
            design_state TEXT NOT NULL,
            blueprint TEXT NOT NULL,
            score REAL NOT NULL,
            headline TEXT NOT NULL,
            body TEXT,
            cta TEXT,
            action TEXT,
            file_path TEXT,
            creative_hash TEXT,
            experiment_id TEXT,
            variant_label TEXT,
            score_breakdown_json TEXT,
            metadata_json TEXT,
            human_approved BOOLEAN,
            feedback_label TEXT,
            feedback_notes TEXT,
            format TEXT,
            width INTEGER,
            height INTEGER,
            visual_qa_status TEXT,
            ctr REAL,
            lead_cost REAL,
            impressions INTEGER,
            clicks INTEGER,
            conversions INTEGER,
            spend REAL,
            revenue REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de versões/histórico
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            changes_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        )
    """)

    # Criar índices para campaign_versions
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_campaign_id ON campaign_versions(campaign_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_version ON campaign_versions(version_number)")

    # Tabela de estatísticas agregadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date DATE UNIQUE,
            total_generated INTEGER,
            total_approved INTEGER,
            avg_score REAL,
            avg_ctr REAL,
            avg_lead_cost REAL,
            top_design_state TEXT,
            top_blueprint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de audit log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            campaign_id INTEGER,
            details_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Criar índices para audit_log
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_campaign_id ON audit_log(campaign_id)")

    # Migrações leves para bancos já existentes.
    cursor.execute("PRAGMA table_info(campaigns)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    migrations = {
        "niche": "ALTER TABLE campaigns ADD COLUMN niche TEXT",
        "objective": "ALTER TABLE campaigns ADD COLUMN objective TEXT",
        "action": "ALTER TABLE campaigns ADD COLUMN action TEXT",
        "file_path": "ALTER TABLE campaigns ADD COLUMN file_path TEXT",
        "creative_hash": "ALTER TABLE campaigns ADD COLUMN creative_hash TEXT",
        "experiment_id": "ALTER TABLE campaigns ADD COLUMN experiment_id TEXT",
        "variant_label": "ALTER TABLE campaigns ADD COLUMN variant_label TEXT",
        "score_breakdown_json": "ALTER TABLE campaigns ADD COLUMN score_breakdown_json TEXT",
        "metadata_json": "ALTER TABLE campaigns ADD COLUMN metadata_json TEXT",
        "feedback_label": "ALTER TABLE campaigns ADD COLUMN feedback_label TEXT",
        "feedback_notes": "ALTER TABLE campaigns ADD COLUMN feedback_notes TEXT",
        "format": "ALTER TABLE campaigns ADD COLUMN format TEXT",
        "width": "ALTER TABLE campaigns ADD COLUMN width INTEGER",
        "height": "ALTER TABLE campaigns ADD COLUMN height INTEGER",
        "visual_qa_status": "ALTER TABLE campaigns ADD COLUMN visual_qa_status TEXT",
        "impressions": "ALTER TABLE campaigns ADD COLUMN impressions INTEGER",
        "clicks": "ALTER TABLE campaigns ADD COLUMN clicks INTEGER",
        "conversions": "ALTER TABLE campaigns ADD COLUMN conversions INTEGER",
        "spend": "ALTER TABLE campaigns ADD COLUMN spend REAL",
        "revenue": "ALTER TABLE campaigns ADD COLUMN revenue REAL",
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            cursor.execute(statement)

    # Criar índices para campaigns depois das migrações.
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_client ON campaigns(client)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_niche ON campaigns(niche)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_design_state ON campaigns(design_state)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_blueprint ON campaigns(blueprint)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_format ON campaigns(format)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_experiment_id ON campaigns(experiment_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_visual_qa_status ON campaigns(visual_qa_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_score ON campaigns(score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_campaigns_creative_hash ON campaigns(creative_hash)")

    conn.commit()
    conn.close()


class VisualMemory:
    """Interface principal para persistência de memória visual."""

    def __init__(self):
        _init_database()
        self.db_file = DB_FILE

    def _get_connection(self):
        """Obtém conexão SQLite."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def _build_creative_hash(self, client: str, design_state: str, blueprint: str,
                             headline: str, cta: str = None, file_path: str = None) -> str:
        """Cria chave estável para evitar duplicar a mesma peça em reprocessamentos."""
        payload = "|".join([
            client or "",
            design_state or "",
            blueprint or "",
            headline or "",
            cta or "",
            os.path.basename(file_path or ""),
        ])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_campaign(self, client: str, design_state: str, blueprint: str,
                       score: float, headline: str, body: str = None,
                       cta: str = None, approved: bool = None,
                       ctr: float = None, lead_cost: float = None,
                       niche: str = None, objective: str = None,
                       action: str = None, file_path: str = None,
                       score_breakdown: Dict = None,
                       metadata: Dict = None,
                       format: str = None, width: int = None, height: int = None,
                       visual_qa_status: str = None,
                       experiment_id: str = None,
                       variant_label: str = None,
                       creative_hash: str = None) -> Dict:
        """Registra uma campanha na memória."""
        conn = self._get_connection()
        cursor = conn.cursor()
        creative_hash = creative_hash or self._build_creative_hash(
            client, design_state, blueprint, headline, cta, file_path
        )
        score_breakdown_json = json.dumps(score_breakdown or {}, ensure_ascii=False)
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

        try:
            cursor.execute("""
                INSERT INTO campaigns
                (client, niche, objective, design_state, blueprint, score, headline,
                 body, cta, action, file_path, creative_hash, experiment_id, variant_label, score_breakdown_json,
                 metadata_json, human_approved, format, width, height, visual_qa_status,
                 ctr, lead_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(creative_hash) DO UPDATE SET
                    score=excluded.score,
                    action=excluded.action,
                    experiment_id=COALESCE(excluded.experiment_id, campaigns.experiment_id),
                    variant_label=COALESCE(excluded.variant_label, campaigns.variant_label),
                    score_breakdown_json=excluded.score_breakdown_json,
                    metadata_json=excluded.metadata_json,
                    format=COALESCE(excluded.format, campaigns.format),
                    width=COALESCE(excluded.width, campaigns.width),
                    height=COALESCE(excluded.height, campaigns.height),
                    visual_qa_status=COALESCE(excluded.visual_qa_status, campaigns.visual_qa_status),
                    human_approved=COALESCE(campaigns.human_approved, excluded.human_approved),
                    ctr=COALESCE(excluded.ctr, campaigns.ctr),
                    lead_cost=COALESCE(excluded.lead_cost, campaigns.lead_cost),
                    updated_at=CURRENT_TIMESTAMP
            """, (client, niche, objective, design_state, blueprint, score, headline,
                  body, cta, action, file_path, creative_hash, experiment_id, variant_label, score_breakdown_json,
                  metadata_json, approved, format, width, height, visual_qa_status,
                  ctr, lead_cost))

            campaign_id = cursor.lastrowid
            if not campaign_id:
                cursor.execute("SELECT id FROM campaigns WHERE creative_hash = ?", (creative_hash,))
                campaign_id = cursor.fetchone()["id"]

            # Log na auditoria
            cursor.execute("""
                INSERT INTO audit_log (action, campaign_id, details_json)
                VALUES (?, ?, ?)
            """, ("record_campaign", campaign_id,
                  json.dumps({"client": client, "niche": niche, "score": score, "blueprint": blueprint},
                             ensure_ascii=False)))

            conn.commit()

            return {
                "id": campaign_id,
                "client": client,
                "niche": niche,
                "design_state": design_state,
                "blueprint": blueprint,
                "score": score,
                "headline": headline,
                "action": action,
                "format": format,
                "experiment_id": experiment_id,
                "variant_label": variant_label,
                "visual_qa_status": visual_qa_status,
                "human_approved": approved,
                "creative_hash": creative_hash,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            conn.close()

    def _resolve_campaign_id(self, campaign_id: int = None,
                             creative_hash: str = None,
                             file_path: str = None) -> Optional[int]:
        """Resolve um criativo por id, hash ou caminho de arquivo."""
        if campaign_id:
            return campaign_id

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if creative_hash:
                cursor.execute("SELECT id FROM campaigns WHERE creative_hash = ?", (creative_hash,))
            elif file_path:
                cursor.execute("SELECT id FROM campaigns WHERE file_path = ?", (file_path,))
            else:
                return None
            row = cursor.fetchone()
            return row["id"] if row else None
        finally:
            conn.close()

    def set_human_feedback(self, campaign_id: int = None, approved: bool = None,
                           label: str = None, notes: str = None,
                           creative_hash: str = None,
                           file_path: str = None) -> Dict:
        """
        Registra feedback humano explícito.

        Use quando o usuário aprovar/reprovar uma arte ou preferir um criativo.
        """
        resolved_id = self._resolve_campaign_id(campaign_id, creative_hash, file_path)
        if not resolved_id:
            return {"status": "error", "message": "campaign not found"}

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE campaigns
                SET human_approved = COALESCE(?, human_approved),
                    feedback_label = COALESCE(?, feedback_label),
                    feedback_notes = COALESCE(?, feedback_notes),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (approved, label, notes, resolved_id))

            cursor.execute("""
                INSERT INTO audit_log (action, campaign_id, details_json)
                VALUES (?, ?, ?)
            """, ("human_feedback", resolved_id, json.dumps({
                "approved": approved,
                "label": label,
                "notes": notes,
            }, ensure_ascii=False)))

            conn.commit()
            self.create_snapshot()
            return {
                "status": "success",
                "campaign_id": resolved_id,
                "approved": approved,
                "label": label,
            }
        finally:
            conn.close()

    def record_performance(self, campaign_id: int = None,
                           creative_hash: str = None,
                           file_path: str = None,
                           impressions: int = None,
                           clicks: int = None,
                           conversions: int = None,
                           spend: float = None,
                           revenue: float = None,
                           ctr: float = None,
                           lead_cost: float = None) -> Dict:
        """
        Registra métricas reais de mídia.

        Se CTR ou custo por lead não forem enviados, tenta calcular com
        impressions/clicks/conversions/spend.
        """
        resolved_id = self._resolve_campaign_id(campaign_id, creative_hash, file_path)
        if not resolved_id:
            return {"status": "error", "message": "campaign not found"}

        if ctr is None and impressions and clicks is not None and impressions > 0:
            ctr = clicks / impressions
        if lead_cost is None and spend is not None and conversions and conversions > 0:
            lead_cost = spend / conversions

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE campaigns
                SET impressions = COALESCE(?, impressions),
                    clicks = COALESCE(?, clicks),
                    conversions = COALESCE(?, conversions),
                    spend = COALESCE(?, spend),
                    revenue = COALESCE(?, revenue),
                    ctr = COALESCE(?, ctr),
                    lead_cost = COALESCE(?, lead_cost),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                impressions, clicks, conversions, spend, revenue,
                ctr, lead_cost, resolved_id,
            ))

            cursor.execute("""
                INSERT INTO audit_log (action, campaign_id, details_json)
                VALUES (?, ?, ?)
            """, ("record_performance", resolved_id, json.dumps({
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "spend": spend,
                "revenue": revenue,
                "ctr": ctr,
                "lead_cost": lead_cost,
            }, ensure_ascii=False)))

            conn.commit()
            self.create_snapshot()
            return {
                "status": "success",
                "campaign_id": resolved_id,
                "ctr": ctr,
                "lead_cost": lead_cost,
            }
        finally:
            conn.close()

    def get_experiment_report(self, experiment_id: str) -> Dict:
        """
        Retorna leitura A/B simples por experimento.

        Quando há impressões e conversões em pelo menos duas variantes, calcula
        uma comparação z-score aproximada entre as duas melhores taxas de conversão.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    COALESCE(variant_label, creative_hash, CAST(id AS TEXT)) as variant_label,
                    creative_hash,
                    blueprint,
                    format,
                    score,
                    human_approved,
                    visual_qa_status,
                    COALESCE(impressions, 0) as impressions,
                    COALESCE(clicks, 0) as clicks,
                    COALESCE(conversions, 0) as conversions,
                    COALESCE(spend, 0) as spend,
                    COALESCE(revenue, 0) as revenue,
                    ctr,
                    lead_cost,
                    file_path
                FROM campaigns
                WHERE experiment_id = ?
                ORDER BY created_at ASC, id ASC
            """, (experiment_id,))
            rows = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

        variants = []
        for row in rows:
            impressions = int(row.get("impressions") or 0)
            conversions = int(row.get("conversions") or 0)
            clicks = int(row.get("clicks") or 0)
            spend = float(row.get("spend") or 0)
            revenue = float(row.get("revenue") or 0)
            conversion_rate = conversions / impressions if impressions > 0 else None
            click_rate = clicks / impressions if impressions > 0 else row.get("ctr")
            cost_per_conversion = spend / conversions if conversions > 0 else row.get("lead_cost")
            variants.append({
                **row,
                "conversion_rate": conversion_rate,
                "click_rate": click_rate,
                "cost_per_conversion": cost_per_conversion,
                "roas": revenue / spend if spend > 0 else None,
            })

        variants.sort(
            key=lambda item: (
                item["conversion_rate"] is not None,
                item["conversion_rate"] or 0,
                item.get("score") or 0,
            ),
            reverse=True,
        )

        significance = {"status": "needs_more_data"}
        measurable = [
            item for item in variants
            if item.get("impressions", 0) > 0 and item.get("conversions") is not None
        ]
        if len(measurable) >= 2:
            a, b = measurable[0], measurable[1]
            n1, n2 = a["impressions"], b["impressions"]
            x1, x2 = a["conversions"], b["conversions"]
            p1 = x1 / n1 if n1 else 0
            p2 = x2 / n2 if n2 else 0
            pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) else 0
            variance = pooled * (1 - pooled) * ((1 / n1) + (1 / n2)) if n1 and n2 else 0
            z_score = (p1 - p2) / (variance ** 0.5) if variance > 0 else 0
            significance = {
                "status": "significant" if abs(z_score) >= 1.96 else "inconclusive",
                "winner": a["variant_label"] if p1 >= p2 else b["variant_label"],
                "baseline": b["variant_label"],
                "z_score": round(z_score, 3),
                "confidence_approx": "95%" if abs(z_score) >= 1.96 else "<95%",
            }

        return {
            "experiment_id": experiment_id,
            "variant_count": len(variants),
            "winner": variants[0] if variants else None,
            "variants": variants,
            "significance": significance,
        }

    def get_winning_creatives(self, niche: str = None, design_state: str = None,
                              limit: int = 10) -> List[Dict]:
        """Retorna criativos vencedores combinando aprovação, score e métricas reais."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT *,
                    (
                        score
                        + CASE WHEN human_approved = 1 THEN 12 ELSE 0 END
                        + COALESCE(ctr, 0) * 100
                        + CASE WHEN lead_cost IS NOT NULL THEN MAX(0, 20 - lead_cost) ELSE 0 END
                        + COALESCE(conversions, 0) * 2
                    ) as learning_score
                FROM campaigns
                WHERE 1=1
            """
            params = []
            if niche:
                query += " AND lower(COALESCE(niche, '')) = lower(?)"
                params.append(niche)
            if design_state:
                query += " AND design_state = ?"
                params.append(design_state)
            query += " ORDER BY learning_score DESC, updated_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def record_creative_batch(self, creatives: List[Dict], context: Dict = None,
                              auto_approve_actions: bool = True) -> List[Dict]:
        """Registra um lote rankeado de criativos e devolve os registros salvos."""
        context = context or {}
        experiment_id = context.get("experiment_id")
        saved = []
        for creative in creatives:
            action = creative.get("action")
            approved = True if auto_approve_actions and action == "auto_approve" else None
            visual_qa = creative.get("visual_qa") or {}
            variant_label = creative.get("variant_label")
            if not variant_label:
                angle_number = int(creative.get("angle_index", 0)) + 1
                variant_label = f"{creative.get('format') or 'creative'}-v{angle_number}"
            saved.append(self.record_campaign(
                client=creative.get("client") or context.get("client_name") or context.get("client") or "Cliente Geral",
                niche=creative.get("niche") or context.get("niche"),
                objective=creative.get("objective") or context.get("objective"),
                design_state=creative.get("design_state") or context.get("design_state", "authority"),
                blueprint=creative.get("blueprint", "unknown"),
                score=float(creative.get("score", 0)),
                headline=creative.get("headline", ""),
                body=creative.get("body"),
                cta=creative.get("cta"),
                action=action,
                file_path=creative.get("file"),
                score_breakdown=creative.get("score_breakdown"),
                metadata={
                    "angle_index": creative.get("angle_index"),
                    "file": creative.get("file"),
                    "format": creative.get("format"),
                    "width": creative.get("width"),
                    "height": creative.get("height"),
                    "template_family": creative.get("template_family"),
                    "visual_qa": visual_qa,
                    "visual_qa_status": visual_qa.get("status"),
                    "source": "creative_ranker",
                },
                format=creative.get("format"),
                width=creative.get("width"),
                height=creative.get("height"),
                visual_qa_status=visual_qa.get("status"),
                experiment_id=creative.get("experiment_id") or experiment_id,
                variant_label=variant_label,
                approved=approved,
            ))
        self.create_snapshot()
        return saved

    def get_best_blueprint_for_state(self, design_state: str, niche: str = None) -> Optional[str]:
        """Retorna blueprint com melhor performance para um design state e nicho opcional."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if niche:
                cursor.execute("""
                    SELECT blueprint, AVG(score) as avg_score, COUNT(*) as total
	                    FROM campaigns
	                    WHERE design_state = ?
	                      AND lower(COALESCE(niche, '')) = lower(?)
	                      AND (human_approved = 1 OR action = 'auto_approve')
                          AND COALESCE(visual_qa_status, '') != 'fail'
	                    GROUP BY blueprint
                    ORDER BY avg_score DESC, total DESC
                    LIMIT 1
                """, (design_state, niche))
            else:
                cursor.execute("""
                    SELECT blueprint, AVG(score) as avg_score, COUNT(*) as total
	                    FROM campaigns
	                    WHERE design_state = ?
                          AND (human_approved = 1 OR action = 'auto_approve')
                          AND COALESCE(visual_qa_status, '') != 'fail'
	                    GROUP BY blueprint
                    ORDER BY avg_score DESC, total DESC
                    LIMIT 1
                """, (design_state,))

            row = cursor.fetchone()
            return row["blueprint"] if row else None
        finally:
            conn.close()

    def get_learning_context(self, niche: str = None, design_state: str = None,
                             limit: int = 5) -> Dict:
        """Resumo acionável do que a memória já aprendeu para orientar novas criações."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT *
                FROM campaigns
                WHERE 1=1
            """
            params = []
            if niche:
                query += " AND lower(COALESCE(niche, '')) = lower(?)"
                params.append(niche)
            if design_state:
                query += " AND design_state = ?"
                params.append(design_state)
            query += " ORDER BY score DESC, created_at DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            top = [dict(row) for row in cursor.fetchall()]

            blueprint_query = """
                SELECT blueprint, COUNT(*) as total, AVG(score) as avg_score
                FROM campaigns
                WHERE 1=1
            """
            blueprint_params = []
            if niche:
                blueprint_query += " AND lower(COALESCE(niche, '')) = lower(?)"
                blueprint_params.append(niche)
            if design_state:
                blueprint_query += " AND design_state = ?"
                blueprint_params.append(design_state)
            blueprint_query += """
                GROUP BY blueprint
                ORDER BY avg_score DESC, total DESC
                LIMIT ?
            """
            blueprint_params.append(limit)
            cursor.execute(blueprint_query, blueprint_params)
            blueprints = [dict(row) for row in cursor.fetchall()]

            return {
                "niche": niche,
                "design_state": design_state,
                "best_blueprint": blueprints[0]["blueprint"] if blueprints else None,
                "blueprints": blueprints,
                "top_creatives": top,
                "stats": self.get_stats(),
            }
        finally:
            conn.close()

    def get_stats(self) -> Dict:
        """Retorna estatísticas globais."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Total gerado
            cursor.execute("SELECT COUNT(*) as count FROM campaigns")
            total_gen = cursor.fetchone()["count"]

            # Total aprovado
            cursor.execute(
                "SELECT COUNT(*) as count FROM campaigns WHERE human_approved = 1"
            )
            total_app = cursor.fetchone()["count"]

            # Score médio
            cursor.execute("SELECT AVG(score) as avg_score FROM campaigns WHERE score IS NOT NULL")
            avg_score = cursor.fetchone()["avg_score"] or 0

            # CTR médio
            cursor.execute("SELECT AVG(ctr) as avg_ctr FROM campaigns WHERE ctr IS NOT NULL")
            avg_ctr = cursor.fetchone()["avg_ctr"] or 0

            # Lead cost médio
            cursor.execute(
                "SELECT AVG(lead_cost) as avg_cost FROM campaigns WHERE lead_cost IS NOT NULL"
            )
            avg_cost = cursor.fetchone()["avg_cost"] or 0

            # Design state mais usado
            cursor.execute("""
                SELECT design_state, COUNT(*) as count
                FROM campaigns
                GROUP BY design_state
                ORDER BY count DESC
                LIMIT 1
            """)
            top_state_row = cursor.fetchone()
            top_state = top_state_row["design_state"] if top_state_row else None

            # Blueprint mais usado
            cursor.execute("""
                SELECT blueprint, COUNT(*) as count
                FROM campaigns
                GROUP BY blueprint
                ORDER BY count DESC
                LIMIT 1
            """)
            top_blueprint_row = cursor.fetchone()
            top_blueprint = top_blueprint_row["blueprint"] if top_blueprint_row else None

            return {
                "total_generated": total_gen,
                "total_approved": total_app,
                "approval_rate": round(total_app / total_gen * 100, 1) if total_gen > 0 else 0,
                "avg_score": round(avg_score, 2),
                "avg_ctr": round(avg_ctr, 4),
                "avg_lead_cost": round(avg_cost, 2),
                "top_design_state": top_state,
                "top_blueprint": top_blueprint,
                "snapshot_at": datetime.now().isoformat()
            }
        finally:
            conn.close()

    def get_history(self, limit: int = 10, client: str = None,
                   design_state: str = None) -> List[Dict]:
        """Retorna histórico de campanhas com filtros opcionais."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM campaigns WHERE 1=1"
            params = []

            if client:
                query += " AND client = ?"
                params.append(client)

            if design_state:
                query += " AND design_state = ?"
                params.append(design_state)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_performance_by_state(self) -> Dict[str, Dict]:
        """Retorna performance agregada por design state."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    design_state,
                    COUNT(*) as total,
                    SUM(CASE WHEN human_approved = 1 THEN 1 ELSE 0 END) as approved,
                    AVG(score) as avg_score,
                    AVG(ctr) as avg_ctr
                FROM campaigns
                GROUP BY design_state
                ORDER BY avg_score DESC
            """)

            rows = cursor.fetchall()
            result = {}

            for row in rows:
                result[row["design_state"]] = {
                    "total_generated": row["total"],
                    "total_approved": row["approved"] or 0,
                    "avg_score": round(row["avg_score"], 2) if row["avg_score"] else 0,
                    "avg_ctr": round(row["avg_ctr"], 4) if row["avg_ctr"] else 0
                }

            return result
        finally:
            conn.close()

    def get_trending_blueprints(self, limit: int = 5) -> List[Tuple[str, int, float]]:
        """Retorna blueprints com melhor performance."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    blueprint,
                    COUNT(*) as count,
                    AVG(score) as avg_score
                FROM campaigns
                WHERE human_approved = 1
                GROUP BY blueprint
                ORDER BY avg_score DESC, count DESC
                LIMIT ?
            """, (limit,))

            return [(row["blueprint"], row["count"], row["avg_score"])
                    for row in cursor.fetchall()]
        finally:
            conn.close()

    def cleanup_old_records(self, days: int = 90) -> int:
        """Remove registros antigos (older than N days). Retorna count."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute("""
                DELETE FROM campaigns
                WHERE created_at < ?
            """, (cutoff_date,))

            deleted_count = cursor.rowcount

            # Log na auditoria
            cursor.execute("""
                INSERT INTO audit_log (action, details_json)
                VALUES (?, ?)
            """, ("cleanup_old_records",
                  json.dumps({"deleted_count": deleted_count, "older_than_days": days})))

            conn.commit()

            return deleted_count
        finally:
            conn.close()

    def create_snapshot(self) -> Dict:
        """Cria um snapshot de estatísticas no histórico."""
        stats = self.get_stats()
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = datetime.now().date().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO stats_snapshots
                (snapshot_date, total_generated, total_approved, avg_score,
                 avg_ctr, avg_lead_cost, top_design_state, top_blueprint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                stats["total_generated"],
                stats["total_approved"],
                stats["avg_score"],
                stats["avg_ctr"],
                stats["avg_lead_cost"],
                stats["top_design_state"],
                stats["top_blueprint"]
            ))

            conn.commit()
            return {"status": "snapshot_created", "date": today}
        finally:
            conn.close()

    def export_to_json(self, output_path: str = None) -> str:
        """Exporta memória inteira para JSON (backup)."""
        if output_path is None:
            output_path = os.path.join(BACKUP_DIR,
                                      f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
            campaigns = [dict(row) for row in cursor.fetchall()]

            # Serializar timestamps
            for camp in campaigns:
                if isinstance(camp["created_at"], str):
                    pass  # Já é string
                else:
                    camp["created_at"] = camp["created_at"].isoformat()
                if isinstance(camp["updated_at"], str):
                    pass
                else:
                    camp["updated_at"] = camp["updated_at"].isoformat()

            backup_data = {
                "exported_at": datetime.now().isoformat(),
                "stats": self.get_stats(),
                "campaigns": campaigns
            }

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)

            return output_path
        finally:
            conn.close()

    def backup_database(self, output_path: str = None) -> str:
        """Cria uma cópia consistente do SQLite usando a API nativa de backup."""
        if output_path is None:
            output_path = os.path.join(
                BACKUP_DIR,
                f"visual_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        source = self._get_connection()
        target = sqlite3.connect(output_path)
        try:
            source.backup(target)
            return output_path
        finally:
            target.close()
            source.close()

    def create_full_backup(self, output_dir: str = None) -> Dict:
        """Gera backup JSON + réplica SQLite e registra no audit log."""
        output_dir = output_dir or BACKUP_DIR
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(output_dir, f"visual_memory_{timestamp}.json")
        sqlite_path = os.path.join(output_dir, f"visual_memory_{timestamp}.db")

        exported_json = self.export_to_json(json_path)
        exported_db = self.backup_database(sqlite_path)

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO audit_log (action, details_json)
                VALUES (?, ?)
            """, ("create_full_backup", json.dumps({
                "json_path": exported_json,
                "sqlite_path": exported_db,
            }, ensure_ascii=False)))
            conn.commit()
        finally:
            conn.close()

        return {
            "status": "success",
            "json_path": exported_json,
            "sqlite_path": exported_db,
            "created_at": datetime.now().isoformat(),
        }


# Singleton instance
_instance = None

def get_memory() -> VisualMemory:
    """Obtém instância singleton de VisualMemory."""
    global _instance
    if _instance is None:
        _instance = VisualMemory()
    return _instance


# Backward compatibility functions
def record_campaign(client: str, design_state: str, blueprint: str,
                   score: float, headline: str, approved: bool = None,
                   ctr: float = None, lead_cost: float = None,
                   body: str = None, cta: str = None, niche: str = None,
                   objective: str = None, action: str = None,
                   file_path: str = None, score_breakdown: Dict = None,
                   metadata: Dict = None, format: str = None,
                   width: int = None, height: int = None,
                   visual_qa_status: str = None,
                   experiment_id: str = None,
                   variant_label: str = None) -> Dict:
    """Wrapper compatível com a API anterior."""
    return get_memory().record_campaign(
        client, design_state, blueprint, score, headline,
        body=body, cta=cta, approved=approved, ctr=ctr, lead_cost=lead_cost,
        niche=niche, objective=objective, action=action, file_path=file_path,
        score_breakdown=score_breakdown, metadata=metadata,
        format=format, width=width, height=height,
        visual_qa_status=visual_qa_status,
        experiment_id=experiment_id,
        variant_label=variant_label,
    )


def get_best_blueprint_for_state(design_state: str, niche: str = None) -> Optional[str]:
    """Wrapper compatível com a API anterior."""
    return get_memory().get_best_blueprint_for_state(design_state, niche=niche)


def get_stats() -> Dict:
    """Wrapper compatível com a API anterior."""
    return get_memory().get_stats()


def get_history(limit: int = 10) -> List[Dict]:
    """Wrapper compatível com a API anterior."""
    return get_memory().get_history(limit=limit)


def set_human_feedback(campaign_id: int = None, approved: bool = None,
                       label: str = None, notes: str = None,
                       creative_hash: str = None,
                       file_path: str = None) -> Dict:
    """Wrapper para feedback humano explícito."""
    return get_memory().set_human_feedback(
        campaign_id=campaign_id,
        approved=approved,
        label=label,
        notes=notes,
        creative_hash=creative_hash,
        file_path=file_path,
    )


def record_performance(campaign_id: int = None,
                       creative_hash: str = None,
                       file_path: str = None,
                       impressions: int = None,
                       clicks: int = None,
                       conversions: int = None,
                       spend: float = None,
                       revenue: float = None,
                       ctr: float = None,
                       lead_cost: float = None) -> Dict:
    """Wrapper para registrar performance real de mídia."""
    return get_memory().record_performance(
        campaign_id=campaign_id,
        creative_hash=creative_hash,
        file_path=file_path,
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        spend=spend,
        revenue=revenue,
        ctr=ctr,
        lead_cost=lead_cost,
    )


def get_experiment_report(experiment_id: str) -> Dict:
    """Wrapper para relatório A/B de um experimento."""
    return get_memory().get_experiment_report(experiment_id)


def create_full_backup(output_dir: str = None) -> Dict:
    """Wrapper para backup JSON + SQLite."""
    return get_memory().create_full_backup(output_dir=output_dir)
