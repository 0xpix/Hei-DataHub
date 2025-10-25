"""
Visual demonstration of the enhanced badge system.
This shows how different filter types are now displayed with distinctive emoji.
"""

# Example search queries and their resulting badges:

EXAMPLES = {
    "Simple field filter": {
        "query": "project:ML-Research",
        "badges": ["🏷 project:ML-Research"],
        "description": "Standard field filter with label emoji"
    },

    "Exact match": {
        "query": "format=CSV",
        "badges": ["🎯 format=CSV"],
        "description": "Exact match with target emoji"
    },

    "Numeric comparison (greater)": {
        "query": "size>100MB",
        "badges": ["📈 size>100MB"],
        "description": "Greater than with upward trend emoji"
    },

    "Numeric comparison (less)": {
        "query": "year<2020",
        "badges": ["📉 year<2020"],
        "description": "Less than with downward trend emoji"
    },

    "Range query": {
        "query": "year>=2020 year<=2023",
        "badges": ["⬆️ year>=2020", "⬇️ year<=2023"],
        "description": "Range with up/down arrow emoji"
    },

    "Free text search": {
        "query": "neural network",
        "badges": ["📝 neural", "📝 network"],
        "description": "Free text terms with memo emoji"
    },

    "Complex mixed query": {
        "query": "project:DeepLearning type=model size>50MB neural network",
        "badges": [
            "🏷 project:DeepLearning",
            "🎯 type=model",
            "📈 size>50MB",
            "📝 neural",
            "📝 network"
        ],
        "description": "Mix of field filters, comparisons, and free text"
    }
}


def print_examples():
    """Print visual examples of badge rendering."""
    print("=" * 80)
    print("ENHANCED BADGE SYSTEM - VISUAL EXAMPLES")
    print("=" * 80)
    print()

    for title, example in EXAMPLES.items():
        print(f"\n{title.upper()}")
        print("-" * 80)
        print(f"Query:       {example['query']}")
        print(f"Badges:      {' '.join(example['badges'])}")
        print(f"Description: {example['description']}")

    print("\n" + "=" * 80)
    print("EMOJI LEGEND")
    print("=" * 80)
    print("🏷  Field filter (contains)")
    print("🎯  Exact match (equals)")
    print("📈  Greater than")
    print("📉  Less than")
    print("⬆️  Greater than or equal")
    print("⬇️  Less than or equal")
    print("📝  Free text search term")
    print()


if __name__ == "__main__":
    print_examples()
