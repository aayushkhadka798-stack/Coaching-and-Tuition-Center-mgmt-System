export default function ErrorState({ title = 'Unable to load data', description = 'Please try again.' }) {
  return <div className="error-state"><strong>{title}</strong><p>{description}</p></div>
}
