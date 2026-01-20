// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ios-networking",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "ios-networking",
            targets: ["ios-networking"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "ios-networking",
            dependencies: [],
            path: "Sources/ios-networking"
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["ios-networking"],
            path: "Sources/Examples/Example1"
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["ios-networking"],
            path: "Sources/Examples/Example2"
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["ios-networking"],
            path: "Sources/Examples/Example3"
        ),

        // Test target
        .testTarget(
            name: "ios-networkingTests",
            dependencies: ["ios-networking"],
            path: "Tests/ios-networkingTests"
        )
    ]
)
