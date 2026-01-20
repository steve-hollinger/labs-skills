// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Swift6Concurrency",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "Swift6Concurrency",
            targets: ["Swift6Concurrency"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "Swift6Concurrency",
            dependencies: [],
            path: "Sources/Swift6Concurrency",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency")
            ]
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["Swift6Concurrency"],
            path: "Sources/Examples/Example1",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency")
            ]
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["Swift6Concurrency"],
            path: "Sources/Examples/Example2",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency")
            ]
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["Swift6Concurrency"],
            path: "Sources/Examples/Example3",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency")
            ]
        ),

        // Test target
        .testTarget(
            name: "Swift6ConcurrencyTests",
            dependencies: ["Swift6Concurrency"],
            path: "Tests/Swift6ConcurrencyTests",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency")
            ]
        )
    ]
)
