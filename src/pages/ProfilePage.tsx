import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Profile</h1>
        <p className={styles.info}><b>Username:</b> {user.username}</p>
        <p className={styles.role}><b>Role:</b> {user.role}</p>
        <button className={styles.button} onClick={() => navigate('/')}>Back to Home</button>
      </div>
    </div>
  );
};

export default ProfilePage;
