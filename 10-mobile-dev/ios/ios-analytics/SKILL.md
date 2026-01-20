---
name: implementing-ios-analytics
description: Implement iOS analytics with V2 impression tracking, event analytics, and shelf field patterns. Use when adding analytics or tracking impressions.
---

# iOS Analytics

## Quick Start
```swift
// V2 Impression tracking
struct OfferCardView: View {
    let offer: Offer
    let shelfContext: ShelfContext

    var body: some View {
        OfferCard(offer: offer)
            .onAppear {
                Analytics.trackImpression(
                    event: .sectionImpressionV2,
                    offerId: offer.id,
                    shelfId: shelfContext.shelfId,
                    position: shelfContext.position
                )
            }
    }
}
```

## Key Points
- V2 impression framework
- Shelf context fields
- Action bar tracking
- Section impressions

## Common Mistakes
1. **Missing shelf fields** - Always include shelfId, position in offer events
2. **Wrong impression event** - Use V2 (sectionImpressionV2) not legacy

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
