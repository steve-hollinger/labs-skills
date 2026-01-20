// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ios-localization",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "ios-localization",
            targets: ["ios-localization"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "ios-localization",
            dependencies: [],
            path: "Sources/ios-localization"
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["ios-localization"],
            path: "Sources/Examples/Example1"
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["ios-localization"],
            path: "Sources/Examples/Example2"
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["ios-localization"],
            path: "Sources/Examples/Example3"
        ),

        // Test target
        .testTarget(
            name: "ios-localizationTests",
            dependencies: ["ios-localization"],
            path: "Tests/ios-localizationTests"
        )
    ]
)
