import type { ReactNode } from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Img: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Easy to Use',
    Img: require('@site/static/img/easy_to_use.png').default,
    description: (
      <>
        Guard was designed to be intuitive and easy to set up, whether you use our CLI tool or REST API.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    Img: require('@site/static/img/focus_on_what_matters.png').default,
    description: (
      <>
        Guard lets you focus on redacting sensitive information, leaving the heavy lifting of natural language processing to us.
      </>
    ),
  },
  {
    title: 'Powered by Presidio',
    Img: require('@site/static/img/powered_by_presidio.png').default,
    description: (
      <>
        Built on top of Microsoft's Presidio, Guard provides reliable data processing.
      </>
    ),
  },
];

function Feature({ title, Img, description }: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img className={styles.featureImg} src={Img} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}