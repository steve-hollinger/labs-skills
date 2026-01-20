import { Example1 } from './examples/Example1'
import { Example2 } from './examples/Example2'
import { Example3 } from './examples/Example3'

function App() {
  return (
    <div className="app">
      <h1>{{SKILL_NAME}} Examples</h1>

      <section>
        <h2>Example 1: Basic Usage</h2>
        <Example1 />
      </section>

      <section>
        <h2>Example 2: Intermediate Pattern</h2>
        <Example2 />
      </section>

      <section>
        <h2>Example 3: Advanced Usage</h2>
        <Example3 />
      </section>
    </div>
  )
}

export default App
