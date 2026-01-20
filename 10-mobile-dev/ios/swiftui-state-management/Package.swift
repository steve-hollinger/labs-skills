// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "swiftui-state-management",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "swiftui-state-management",
            targets: ["swiftui-state-management"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "swiftui-state-management",
            dependencies: [],
            path: "Sources/swiftui-state-management"
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["swiftui-state-management"],
            path: "Sources/Examples/Example1"
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["swiftui-state-management"],
            path: "Sources/Examples/Example2"
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["swiftui-state-management"],
            path: "Sources/Examples/Example3"
        ),

        // Test target
        .testTarget(
            name: "swiftui-state-managementTests",
            dependencies: ["swiftui-state-management"],
            path: "Tests/swiftui-state-managementTests"
        )
    ]
)
