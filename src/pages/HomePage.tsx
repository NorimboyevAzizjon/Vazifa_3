import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import styles from './HomePage.module.css';

const HomePage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Welcome to Home Page</h1>
        {user ? (
          <>
            <p className={styles.user}>
              Hello, <b>{user.username}</b> <span className={styles.role}>({user.role})</span>
            </p>
            <button className={`${styles.button} ${styles.logout}`} onClick={logout}>Logout</button>
            <br />
            <button className={styles.button} onClick={() => navigate('/profile')}>Go to Profile</button>
            {user.role === 'admin' && (
              <>
                <br />
                <button className={`${styles.button} ${styles.admin}`} onClick={() => navigate('/admin')}>Go to Admin Panel</button>
              </>
            )}
          </>
        ) : (
          <>
            <p style={{ fontSize: 16, marginBottom: 24 }}>Please login to access your profile and admin panel.</p>
            <button className={styles.button} onClick={() => navigate('/login')}>Login</button>
          </>
        )}
      </div>
    </div>
  );
};

export default HomePage;
