// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "swiftui-animations",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "swiftui-animations",
            targets: ["swiftui-animations"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "swiftui-animations",
            dependencies: [],
            path: "Sources/swiftui-animations"
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["swiftui-animations"],
            path: "Sources/Examples/Example1"
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["swiftui-animations"],
            path: "Sources/Examples/Example2"
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["swiftui-animations"],
            path: "Sources/Examples/Example3"
        ),

        // Test target
        .testTarget(
            name: "swiftui-animationsTests",
            dependencies: ["swiftui-animations"],
            path: "Tests/swiftui-animationsTests"
        )
    ]
)
