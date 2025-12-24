import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import styles from './AdminPage.module.css';

const AdminPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Admin Panel</h1>
        <p className={styles.info}>Welcome, <b>{user.username}</b>!</p>
        <p className={styles.role}>You are logged in as <span>admin</span>.</p>
        <button className={styles.button} onClick={() => navigate('/')}>Back to Home</button>
      </div>
    </div>
  );
};

export default AdminPage;
