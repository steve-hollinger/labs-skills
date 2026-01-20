// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "{{PASCAL_NAME}}",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "{{PASCAL_NAME}}",
            targets: ["{{PASCAL_NAME}}"]
        ),
        .executable(name: "Example1", targets: ["Example1"]),
        .executable(name: "Example2", targets: ["Example2"]),
        .executable(name: "Example3", targets: ["Example3"])
    ],
    dependencies: [],
    targets: [
        // Main library target
        .target(
            name: "{{PASCAL_NAME}}",
            dependencies: [],
            path: "Sources/{{PASCAL_NAME}}"
        ),

        // Example executables
        .executableTarget(
            name: "Example1",
            dependencies: ["{{PASCAL_NAME}}"],
            path: "Sources/Examples/Example1"
        ),
        .executableTarget(
            name: "Example2",
            dependencies: ["{{PASCAL_NAME}}"],
            path: "Sources/Examples/Example2"
        ),
        .executableTarget(
            name: "Example3",
            dependencies: ["{{PASCAL_NAME}}"],
            path: "Sources/Examples/Example3"
        ),

        // Test target
        .testTarget(
            name: "{{PASCAL_NAME}}Tests",
            dependencies: ["{{PASCAL_NAME}}"],
            path: "Tests/{{PASCAL_NAME}}Tests"
        )
    ]
)
