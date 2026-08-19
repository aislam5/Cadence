import { useState, useEffect } from "react";

function App(){
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {fetch('http://127.0.0.1:8000/calendar/week')
    .then((response) => response.json())
    .then((data) => setHealthData(data))
    .catch((error) => console.error('Error Fetching health data'));
  },[]);


return(
  <div>
    <h1>Health Status</h1>
    {healthData ? <pre>{JSON.stringify(healthData, null,2)}</pre> : <p>Loading Health Status .....</p>}
  </div>
  );
} 
export default App;