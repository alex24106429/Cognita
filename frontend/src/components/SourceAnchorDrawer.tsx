import React, { useMemo } from 'react';
import {
  Alert,
  Badge,
  Box,
  Drawer,
  Group,
  ScrollArea,
  Text,
  Title,
} from '@mantine/core';
import { IconAlertTriangle, IconInfoCircle, IconShieldCheck } from '@tabler/icons-react';

import type { ThemePalette } from '../types';
import { findAnchor } from '../utils/anchor';

interface Props {
  opened: boolean;
  onClose: () => void;
  anchorText: string;
  blockHeadline?: string;
  fullOriginalText: string;
  palette: ThemePalette;
}

/**
 * Source provenance drawer — the anti-hallucination control.
 *
 * Shows the exact anchor sentence in italics, then renders the full submitted
 * document with that anchor highlighted inline, so a student can audit the
 * surrounding argument rather than trusting a flattened summary.
 */
export const SourceAnchorDrawer: React.FC<Props> = ({
  opened,
  onClose,
  anchorText,
  blockHeadline,
  fullOriginalText,
  palette,
}) => {
  const match = useMemo(
    () => findAnchor(fullOriginalText, anchorText),
    [fullOriginalText, anchorText]
  );

  const renderContext = () => {
    if (!fullOriginalText) {
      return <Text size="sm">No source text available for this session.</Text>;
    }

    if (!match.found) {
      return <Text className="cognita-source-text">{fullOriginalText}</Text>;
    }

    const before = fullOriginalText.slice(0, match.start);
    const highlighted = fullOriginalText.slice(match.start, match.end);
    const after = fullOriginalText.slice(match.end);

    return (
      <Text className="cognita-source-text" style={{ fontSize: 14 }}>
        {before}
        <mark className="cognita-anchor-highlight">{highlighted}</mark>
        {after}
      </Text>
    );
  };

  return (
    <Drawer
      opened={opened}
      onClose={onClose}
      position="right"
      size="xl"
      title={
        <Group gap="xs">
          <IconShieldCheck color={match.found ? '#2B8A3E' : '#E8590C'} size={20} />
          <Title order={4}>Original source verification</Title>
        </Group>
      }
    >
      <Alert color="blue" variant="light" icon={<IconInfoCircle size={16} />} mb="md">
        <Text size="xs">
          <strong>Anti-omission guard.</strong> Compare the restructured block directly against
          the highlighted passage from your original text to inspect nuances, qualifiers and
          boundary conditions that a summary could flatten.
        </Text>
      </Alert>

      <Group gap="xs" mb="xs">
        <Badge color="yellow" variant="light">
          Referenced passage anchor
        </Badge>
        {blockHeadline && (
          <Badge color="indigo" variant="light">
            {blockHeadline}
          </Badge>
        )}
        <Badge color={match.found ? 'green' : 'orange'} variant="light">
          {match.found ? 'Verbatim match confirmed' : 'Unverified anchor'}
        </Badge>
      </Group>

      <Box
        p="sm"
        mb="lg"
        style={{
          borderLeft: '4px solid #F59F00',
          backgroundColor: palette.shortcutBackground,
          borderRadius: 4,
        }}
      >
        <Text fs="italic" size="sm">
          “{anchorText || 'No anchor was generated for this block.'}”
        </Text>
      </Box>

      {!match.found && anchorText && (
        <Alert color="orange" variant="light" icon={<IconAlertTriangle size={16} />} mb="md">
          <Text size="xs">
            This anchor does not appear verbatim in your submitted text. The model may have
            paraphrased it — read the full context below before relying on the block.
          </Text>
        </Alert>
      )}

      <Title order={5} mb="xs">
        Full document context
      </Title>
      <ScrollArea h={480} type="always" offsetScrollbars>
        {renderContext()}
      </ScrollArea>
    </Drawer>
  );
};
