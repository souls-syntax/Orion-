var express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Job = require('../models/Job'); 
const ATS = require('../models/ATS');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
var router = express.Router();

const uploadDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

// Configure Multer to store as temp.pdf
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, 'temp.pdf');
  },
});

const upload = multer({ storage });

router.get('/', async (req, res) => {
  return res.redirect('/login');
})

// GET home page with user's jobs
router.get('/home', async (req, res) => {
  try {
    const userId = req.session.userId;

    // Ensure user is logged in
    if (!userId) {
      return res.status(401).send('User not authenticated!');
    }

    // Fetch the current user's jobs from the database
    const jobs = await Job.find({ user: userId }); // Assuming user ID is stored in req.user._id

    // Render the home page and pass the jobs to the view
    return res.render('home', { jobs });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

/* GET registration page */
router.get('/register', function(req, res) {
  return res.render('register');
});

/* POST registration */
router.post('/register', async (req, res) => {
  try {
    const { name, email, password, confirmPassword, currentJobRole, currentCompany, jobDescription } = req.body;

    if (!name || !email || !password || !confirmPassword || !currentJobRole || !currentCompany) {
      return res.status(400).json({ error: 'Please fill in all fields.' });
    }

    // Check if passwords match
    if (password !== confirmPassword) {
      return res.status(400).send({ error: 'Passwords do not match.' });
    }

    // Check if the email is already registered
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).send({ error: 'Email is already in use.' });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create a new user
    const user = new User({
      name,
      email,
      password: hashedPassword,
      currentJobRole,
      currentCompany,
      jobDescription,
    });

    await user.save();

    return res.status(200).send({ message: 'Registration successful.' });
  } catch (error) {
    console.error(error);
    return res.status(500).send({ error: 'Registration failed. Please try again later.' });
  }
});


/* GET login page. */
router.get('/login', function(req, res) {
  return res.render('login');
});

/* POST login */

router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
      // Validate request body
      if (!email || !password) {
          return res.status(400).json({ error: 'Email and password are required.' });
      }

      // Find the user
      const user = await User.findOne({email});
      if (!user) {
          return res.status(401).json({ error: 'Invalid credentials.' });
      }

      // Verify password
      const isPasswordValid = await bcrypt.compare(password, user.password);
      if (!isPasswordValid) {
          return res.status(401).json({ error: 'Invalid credentials.' });
      }

      // Generate a token (replace 'secret' with an environment variable in production)
      const token = jwt.sign({ email: user.email }, 'secret', { expiresIn: '1h' });
      req.session.userId = user._id;
      req.session.token = token;
      return res.status(200).json({ message: 'Login successful'});
  } catch (error) {
      console.error(error);
      return res.status(500).json({ error: 'Internal server error.' });
  }
});

/* GET add job page. */
router.get('/add/job', function(req, res) {
  return res.render('add_job');
});

// POST route to add a job
router.post('/add/job', async (req, res) => {
  try {
    const { role, company, description, salary, currentSalary, currentExperience } = req.body;

    if (!role || !company || !salary || !currentSalary || !currentExperience) {
      return res.status(401).send('All required parameters are not filled!');
    }

    const userId = req.session.userId;

    // Ensure user is logged in
    if (!userId) {
      return res.status(401).send('User not authenticated!');
    }

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).send('User not found!');
    }

    const data = {
      current_job: user.currentJobRole, 
      current_salary: currentSalary, 
      experience: currentExperience,
      expected_salary: salary, 
      expected_company: company, 
      expected_job_role: role
    }

    const response = await fetch("http://127.0.0.1:5000/job-assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await response.json();
 
    // Create a new Job document
    const newJob = new Job({
      role,
      company,
      description,
      salary,
      aiResponse: result,
      user: userId, // Associating the job with the logged-in user
    });

    // Save the job to the database
    await newJob.save();

    // Redirect to the home page or job dashboard
    return res.status(200).json({ message: "New job created!" });
  } catch (error) {
    console.error(error);
    return res.status(500).send('An error occurred while adding the job!');
  }
});

/* GET ATS page. */
router.get('/ats', async (req, res) => {
  try {
    const userId = req.session.userId;

    // Ensure user is logged in
    if (!userId) {
      return res.status(401).send('User not authenticated!');
    }

    // Fetch the current user's jobs from the database
    const ats = await ATS.find({ user: userId }); // Assuming user ID is stored in req.user._id

    // Render the home page and pass the jobs to the view
    return res.render('ats', { ats });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: 'Internal server error.' });
  }
});

/* GET add ATS page. */
router.get('/add/ats', function(req, res) {
  return res.render('add_ats');
});

// POST route to add a job
router.post('/add/ats', upload.single('pdfFile'), async (req, res) => {
  try {
    const { companyName, jobDescription } = req.body;
    const pdfPath = path.join(uploadDir, 'temp.pdf');

    if (!companyName || !req.file) {
      return res.status(400).send('All required parameters are not filled!');
    }

    const userId = req.session.userId;
    if (!userId) return res.status(401).send('User not authenticated!');
    
    const user = await User.findById(userId);
    if (!user) return res.status(404).send('User not found!');

    const data = {
      company_name: companyName,
      user_job_description: jobDescription,
      pdf_path: pdfPath
    };

    const aiResponse = await fetch("http://127.0.0.1:5000/ats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await aiResponse.json();

    // Read the uploaded file into a Buffer
    const pdfBuffer = fs.readFileSync(pdfPath);

    const newATS = new ATS({
      companyName,
      jobDescription,
      pdfPath,
      pdfBlob: pdfBuffer, // Store as blob here
      aiResponse: result,
      user: userId,
    });

    await newATS.save();

    return res.status(200).json({ message: "New ATS created!" });

  } catch (error) {
    console.error(error);
    return res.status(500).send('An error occurred while adding the job!');
  }
});

/* GET codebot page. */
router.get('/codebot', function(req, res) {
  return res.render('codebotai');
});

// POST Codebot
router.post('/codebot/process', async (req, res) => {
  try {
    const { code } = req.body;

    if (!code) {
      return res.status(400).json({ error: 'Code not provided!' });
    }

    const response = await fetch("http://127.0.0.1:5000/codebot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });

    const result = await response.json(); // Parse the actual data

    return res.status(200).json(result); // Send it back to the frontend
  } catch (error) {
    console.error(error);
    return res.status(500).send('An error occurred while processing codebot ai!');
  }
});

/* GET ATS score page. */
router.get('/ats/:atsId', async (req, res) => {
  try {
    const userId = req.session.userId;
    const { atsId } = req.params;

    if (!userId) return res.status(401).send('User not authenticated!');
    if (!atsId) return res.status(400).send('No reference id is sent!');

    const ats = await ATS.findOne({ user: userId, _id: atsId });
    if (!ats) return res.status(404).send('ATS not found!');

    res.render('ats_output', { ats, pdf: ats.pdfBlob.buffer.toString('base64') });
  } catch (error) {
    console.error(error);
    res.status(500).send('An error occurred while processing CodeBot AI!');
  }
});

/* get jobId page. */
router.get('/job/:jobId', async (req, res) => {
  try {
    const userId = req.session.userId;
    const { jobId } = req.params;

    if (!userId) return res.status(401).send('User not authenticated!');
    if (!jobId) return res.status(400).send('No reference id is sent!');

    const job = await Job.findOne({ user: userId, _id: jobId });
    if (!job) return res.status(404).send('Job not found!');

    res.render('job_output', { job });
  } catch (error) {
    console.error(error);
    res.status(500).send('An error occurred while processing CodeBot AI!');
  }
});

// router.get('*', (req, res) => {
//   return res.redirect('/login');
// })

module.exports = router;
