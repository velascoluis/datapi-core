import Link from 'next/link';
import Image from 'next/image';
import styles from '../styles/Header.module.css';

function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link href="/" className={styles.logoLink}>
          <Image
            src="/images/logo.png"
            alt="DataPi Logo"
            width={200}
            height={40}
            priority
          />
        </Link>
      </div>
      <nav className={styles.nav}>
        <Link href="#features" className={styles.navLink}>
          Features
        </Link>
        
        <Link href="#integrations" className={styles.navLink}>
          Integrations
        </Link>
      </nav>
     
    </header>
  );
}

export default Header;
