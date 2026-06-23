#!/usr/bin/env python3
"""
LLM Integration for Text Analysis
Uses LLM to analyze news articles, case descriptions, and identify entities/relationships.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/llm_analysis.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class EntityExtraction:
    """Extracted entity from text."""

    name: str
    type: str  # person, organization, case, location
    context: str
    confidence: float


@dataclass
class RelationshipExtraction:
    """Extracted relationship from text."""

    source: str
    target: str
    type: str
    evidence: str
    confidence: float


class LLMTextAnalyzer:
    """
    LLM-based text analyzer for extracting entities and relationships.

    Note: This is a template implementation. To use with real LLM:
    1. Install openai or anthropic package
    2. Set API key in environment
    3. Replace mock methods with actual API calls
    """

    def __init__(self, provider: str = "mock"):
        """
        Initialize LLM analyzer.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'mock')
        """
        self.provider = provider
        self.client = None

        if provider == "openai":
            try:
                import openai

                self.client = openai.OpenAI()
                logger.info("Initialized OpenAI client")
            except ImportError:
                logger.warning("openai package not installed, using mock mode")
                self.provider = "mock"
        elif provider == "anthropic":
            try:
                import anthropic

                self.client = anthropic.Anthropic()
                logger.info("Initialized Anthropic client")
            except ImportError:
                logger.warning("anthropic package not installed, using mock mode")
                self.provider = "mock"
        else:
            logger.info("Using mock LLM for development")

    def extract_entities(
        self, text: str, entity_types: List[str] = None
    ) -> List[EntityExtraction]:
        """
        Extract entities from text using LLM.

        Args:
            text: Input text to analyze
            entity_types: Types of entities to extract

        Returns:
            List of extracted entities
        """
        if entity_types is None:
            entity_types = ["person", "organization", "case", "location", "date"]

        if self.provider == "mock":
            return self._mock_entity_extraction(text, entity_types)

        # Real LLM implementation would go here
        # prompt = f"Extract entities ({', '.join(entity_types)}) from: {text}"
        # response = self.client.chat.completions.create(...)
        # Parse response and return entities

        return []

    def _mock_entity_extraction(
        self, text: str, entity_types: List[str]
    ) -> List[EntityExtraction]:
        """Mock entity extraction for development/testing."""
        entities = []

        # Simple keyword-based extraction for demonstration
        keywords = {
            "person": ["法官", "律師", "檢察官", "林欣怡", "羅秉成"],
            "organization": [
                "法律扶助基金會",
                "司法院",
                "廢死聯盟",
                "法扶會",
                "民間司法改革基金會",
            ],
            "case": ["Kaka案", "陳彥翔案", "梁育誌案", "死刑", "無期徒刑"],
            "location": ["台北", "台中", "高雄", "台灣"],
        }

        for entity_type in entity_types:
            type_keywords = keywords.get(entity_type, [])
            for keyword in type_keywords:
                if keyword in text:
                    entities.append(
                        EntityExtraction(
                            name=keyword,
                            type=entity_type,
                            context=text[
                                max(0, text.find(keyword) - 20) : text.find(keyword)
                                + len(keyword)
                                + 20
                            ],
                            confidence=0.7,
                        )
                    )

        return entities

    def extract_relationships(
        self, text: str, entities: List[EntityExtraction]
    ) -> List[RelationshipExtraction]:
        """
        Extract relationships between entities.

        Args:
            text: Input text
            entities: Previously extracted entities

        Returns:
            List of extracted relationships
        """
        if self.provider == "mock":
            return self._mock_relationship_extraction(text, entities)

        # Real LLM implementation
        return []

    def _mock_relationship_extraction(
        self, text: str, entities: List[EntityExtraction]
    ) -> List[RelationshipExtraction]:
        """Mock relationship extraction."""
        relationships = []

        # Define relationship patterns
        patterns = [
            ("法律扶助基金會", "廢死聯盟", "associated_with", "長期合作關係"),
            ("司法院", "法律扶助基金會", "funds", "預算補助"),
            ("法官", "死刑", "opposes", "判決立場"),
            ("律師", "被告", "represents", "辯護關係"),
        ]

        entity_names = [e.name for e in entities]

        for source, target, rel_type, evidence in patterns:
            if source in entity_names and target in entity_names:
                relationships.append(
                    RelationshipExtraction(
                        source=source,
                        target=target,
                        type=rel_type,
                        evidence=evidence,
                        confidence=0.6,
                    )
                )

        return relationships

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (e.g., news article about legal case).

        Args:
            text: Input text

        Returns:
            Sentiment analysis results
        """
        if self.provider == "mock":
            # Simple keyword-based sentiment
            positive_words = ["支持", "贊成", "進步", "公正", "合理"]
            negative_words = ["反對", "批評", "質疑", "不公", "錯誤"]

            pos_count = sum(1 for w in positive_words if w in text)
            neg_count = sum(1 for w in negative_words if w in text)

            total = pos_count + neg_count
            if total == 0:
                sentiment = "neutral"
                score = 0.5
            elif pos_count > neg_count:
                sentiment = "positive"
                score = pos_count / total
            else:
                sentiment = "negative"
                score = neg_count / total

            return {
                "sentiment": sentiment,
                "score": score,
                "positive_keywords": pos_count,
                "negative_keywords": neg_count,
                "confidence": 0.6 if total > 0 else 0.3,
            }

        return {"sentiment": "unknown", "score": 0.5, "confidence": 0.0}

    def classify_topic(
        self, text: str, topics: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Classify text into predefined topics.

        Args:
            text: Input text
            topics: List of topic categories

        Returns:
            List of (topic, confidence) tuples
        """
        if topics is None:
            topics = ["死刑", "司法改革", "法律扶助", "人權", "預算", "採購"]

        results = []
        for topic in topics:
            if topic in text:
                results.append((topic, 0.8))
            elif self._related_keyword_match(text, topic):
                results.append((topic, 0.5))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def _related_keyword_match(self, text: str, topic: str) -> bool:
        """Check for related keywords to a topic."""
        related = {
            "死刑": ["無期徒刑", "終身監禁", "廢死", "執行", "槍決"],
            "司法改革": ["司法院", "法官", "制度改革", "透明度"],
            "法律扶助": ["法扶", "律師", "辯護", "訴訟", "弱勢"],
            "人權": ["權利", "公平", "正義", "平等"],
            "預算": ["經費", "補助", "撥款", "財政"],
            "採購": ["招標", "投標", "契約", "廠商"],
        }

        keywords = related.get(topic, [])
        return any(kw in text for kw in keywords)

    def analyze_news_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a news article.

        Args:
            article: Article dictionary with 'title', 'content', 'url', 'date'

        Returns:
            Analysis results with entities, relationships, sentiment, topics
        """
        text = f"{article.get('title', '')} {article.get('content', '')}"

        # Extract information
        entities = self.extract_entities(text)
        relationships = self.extract_relationships(text, entities)
        sentiment = self.analyze_sentiment(text)
        topics = self.classify_topic(text)

        # Calculate overall confidence
        entity_conf = (
            sum(e.confidence for e in entities) / len(entities) if entities else 0
        )
        rel_conf = (
            sum(r.confidence for r in relationships) / len(relationships)
            if relationships
            else 0
        )
        overall_conf = (entity_conf + rel_conf + sentiment.get("confidence", 0)) / 3

        result = {
            "article_id": article.get("id", "unknown"),
            "analysis_date": datetime.now().isoformat(),
            "entities": [
                {"name": e.name, "type": e.type, "confidence": e.confidence}
                for e in entities
            ],
            "relationships": [
                {
                    "source": r.source,
                    "target": r.target,
                    "type": r.type,
                    "confidence": r.confidence,
                }
                for r in relationships
            ],
            "sentiment": sentiment,
            "topics": [{"topic": t, "confidence": c} for t, c in topics],
            "overall_confidence": round(overall_conf, 3),
            "llm_provider": self.provider,
        }

        logger.info(
            f"Analyzed article {article.get('id', 'unknown')}: {len(entities)} entities, "
            f"{len(relationships)} relationships, sentiment={sentiment.get('sentiment')}"
        )

        return result

    def batch_analyze(
        self, articles: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple articles in batch.

        Args:
            articles: List of article dictionaries
            output_file: Optional file to save results

        Returns:
            List of analysis results
        """
        results = []

        for i, article in enumerate(articles):
            try:
                logger.info(
                    f"Analyzing article {i + 1}/{len(articles)}: {article.get('title', 'Untitled')[:50]}..."
                )
                result = self.analyze_news_article(article)
                results.append(result)
            except Exception as e:
                logger.error(
                    f"Error analyzing article {article.get('id', 'unknown')}: {e}"
                )
                results.append(
                    {
                        "article_id": article.get("id", "unknown"),
                        "error": str(e),
                        "status": "failed",
                    }
                )

        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "analysis_date": datetime.now().isoformat(),
                        "total_articles": len(articles),
                        "successful": len([r for r in results if "error" not in r]),
                        "failed": len([r for r in results if "error" in r]),
                        "results": results,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Saved analysis results to {output_file}")

        return results


def main():
    """CLI for LLM text analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="LLM text analysis for budget tracker")
    parser.add_argument(
        "--provider",
        choices=["mock", "openai", "anthropic"],
        default="mock",
        help="LLM provider",
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Input JSON file with articles"
    )
    parser.add_argument("--output", "-o", help="Output file for analysis results")
    parser.add_argument(
        "--extract-entities", action="store_true", help="Extract entities only"
    )

    args = parser.parse_args()

    try:
        # Initialize analyzer
        analyzer = LLMTextAnalyzer(provider=args.provider)

        # Load articles
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
            articles = data.get("articles", [])

        if not articles:
            logger.error("No articles found in input file")
            sys.exit(1)

        logger.info(f"Loaded {len(articles)} articles for analysis")

        # Analyze
        if args.extract_entities:
            # Entity extraction only
            for article in articles:
                entities = analyzer.extract_entities(article.get("content", ""))
                print(f"\n{article.get('title', 'Untitled')}")
                for e in entities:
                    print(f"  - [{e.type}] {e.name} (confidence: {e.confidence:.2f})")
        else:
            # Full analysis
            output_file = (
                args.output
                or f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            results = analyzer.batch_analyze(articles, output_file)

            # Summary
            successful = len([r for r in results if "error" not in r])
            print(f"\n{'=' * 60}")
            print("LLM Analysis Complete")
            print(f"{'=' * 60}")
            print(f"Total articles: {len(articles)}")
            print(f"Successful: {successful}")
            print(f"Failed: {len(articles) - successful}")
            print(f"Output: {output_file}")
            print(f"{'=' * 60}\n")

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
